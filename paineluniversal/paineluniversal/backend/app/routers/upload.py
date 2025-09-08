"""
Router para upload de arquivos
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import uuid
from datetime import datetime
import shutil
from pathlib import Path

from ..database import get_db
from ..models import Usuario, Produto
from ..auth_functions import obter_usuario_atual

router = APIRouter()

# Configuração de diretórios
UPLOAD_DIR = Path("uploads")
IMAGE_DIR = UPLOAD_DIR / "images"
FILE_DIR = UPLOAD_DIR / "files"
TEMP_DIR = UPLOAD_DIR / "temp"

# Criar diretórios se não existirem
for directory in [UPLOAD_DIR, IMAGE_DIR, FILE_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Tipos de arquivo permitidos
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
ALLOWED_FILE_TYPES = ["application/pdf", "application/msword", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                      "application/vnd.ms-excel", 
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

def validate_file_type(file: UploadFile, allowed_types: List[str]) -> bool:
    """Validar tipo de arquivo"""
    return file.content_type in allowed_types

def generate_unique_filename(original_filename: str) -> str:
    """Gerar nome único para arquivo"""
    ext = original_filename.split(".")[-1] if "." in original_filename else ""
    unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return f"{unique_name}.{ext}" if ext else unique_name

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    entity_type: Optional[str] = Form("produto"),
    entity_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Upload de imagem para produtos ou outras entidades"""
    
    # Validar tipo de arquivo
    if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido. Use: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validar tamanho (máximo 5MB)
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 5MB")
    
    # Resetar posição do arquivo
    await file.seek(0)
    
    # Gerar nome único
    filename = generate_unique_filename(file.filename)
    file_path = IMAGE_DIR / filename
    
    # Salvar arquivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    finally:
        await file.close()
    
    # Construir URL relativa
    relative_url = f"/uploads/images/{filename}"
    
    # Se associado a uma entidade, atualizar no banco
    if entity_type == "produto" and entity_id:
        produto = db.query(Produto).filter(Produto.id == entity_id).first()
        if produto:
            produto.imagem_url = relative_url
            db.commit()
    
    return {
        "success": True,
        "filename": filename,
        "url": relative_url,
        "size": file_size,
        "type": file.content_type,
        "entity_type": entity_type,
        "entity_id": entity_id
    }

@router.post("/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form("general"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Upload de arquivo geral (PDF, DOC, XLS)"""
    
    # Validar tipo de arquivo
    if not validate_file_type(file, ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido. Use: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    # Validar tamanho (máximo 10MB)
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 10MB")
    
    # Resetar posição do arquivo
    await file.seek(0)
    
    # Gerar nome único
    filename = generate_unique_filename(file.filename)
    file_path = FILE_DIR / filename
    
    # Salvar arquivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    finally:
        await file.close()
    
    # Construir URL relativa
    relative_url = f"/uploads/files/{filename}"
    
    return {
        "success": True,
        "filename": filename,
        "url": relative_url,
        "size": file_size,
        "type": file.content_type,
        "category": category,
        "uploaded_by": current_user.nome,
        "uploaded_at": datetime.now().isoformat()
    }

@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Upload de múltiplos arquivos"""
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Máximo 10 arquivos por vez")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Determinar tipo e diretório
            is_image = validate_file_type(file, ALLOWED_IMAGE_TYPES)
            is_document = validate_file_type(file, ALLOWED_FILE_TYPES)
            
            if not is_image and not is_document:
                errors.append({
                    "filename": file.filename,
                    "error": "Tipo de arquivo não permitido"
                })
                continue
            
            # Validar tamanho
            contents = await file.read()
            file_size = len(contents)
            max_size = 5 * 1024 * 1024 if is_image else 10 * 1024 * 1024
            
            if file_size > max_size:
                errors.append({
                    "filename": file.filename,
                    "error": f"Arquivo muito grande. Máximo: {max_size // (1024*1024)}MB"
                })
                continue
            
            await file.seek(0)
            
            # Gerar nome e salvar
            filename = generate_unique_filename(file.filename)
            directory = IMAGE_DIR if is_image else FILE_DIR
            file_path = directory / filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Adicionar à lista de sucesso
            uploaded_files.append({
                "filename": filename,
                "original_name": file.filename,
                "url": f"/uploads/{'images' if is_image else 'files'}/{filename}",
                "size": file_size,
                "type": file.content_type
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
        finally:
            await file.close()
    
    return {
        "success": len(uploaded_files) > 0,
        "uploaded": uploaded_files,
        "errors": errors,
        "summary": {
            "total": len(files),
            "successful": len(uploaded_files),
            "failed": len(errors)
        }
    }

@router.post("/produtos/{produto_id}/upload-image")
async def upload_product_image(
    produto_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Upload de imagem específica para produto"""
    
    # Verificar se produto existe
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Validar tipo de arquivo
    if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
        raise HTTPException(
            status_code=400,
            detail="Apenas imagens são permitidas (JPEG, PNG, GIF, WebP)"
        )
    
    # Processar upload
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Imagem muito grande. Máximo: 5MB")
    
    await file.seek(0)
    
    # Salvar arquivo
    filename = generate_unique_filename(file.filename)
    file_path = IMAGE_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Atualizar produto
        relative_url = f"/uploads/images/{filename}"
        produto.imagem_url = relative_url
        db.commit()
        
        return {
            "success": True,
            "produto_id": produto_id,
            "produto_nome": produto.nome,
            "imagem_url": relative_url,
            "filename": filename,
            "size": file_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagem: {str(e)}")
    finally:
        await file.close()

@router.delete("/uploads/{file_type}/{filename}")
async def delete_uploaded_file(
    file_type: str,
    filename: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Deletar arquivo enviado"""
    
    if file_type not in ["images", "files"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'images' ou 'files'")
    
    # Verificar permissão (apenas admin pode deletar)
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar arquivos")
    
    # Construir caminho
    directory = IMAGE_DIR if file_type == "images" else FILE_DIR
    file_path = directory / filename
    
    # Verificar se arquivo existe
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    try:
        # Deletar arquivo
        os.remove(file_path)
        
        # Se for imagem de produto, limpar referência no banco
        if file_type == "images":
            produtos = db.query(Produto).filter(
                Produto.imagem_url.like(f"%{filename}%")
            ).all()
            
            for produto in produtos:
                produto.imagem_url = None
            
            if produtos:
                db.commit()
        
        return {
            "success": True,
            "message": "Arquivo deletado com sucesso",
            "filename": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar arquivo: {str(e)}")

@router.get("/uploads/list/{file_type}")
async def list_uploaded_files(
    file_type: str,
    skip: int = 0,
    limit: int = 50,
    current_user: Usuario = Depends(obter_usuario_atual)
):
    """Listar arquivos enviados"""
    
    if file_type not in ["images", "files", "all"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'images', 'files' ou 'all'")
    
    files_list = []
    
    # Determinar diretórios para buscar
    directories = []
    if file_type in ["images", "all"]:
        directories.append(("images", IMAGE_DIR))
    if file_type in ["files", "all"]:
        directories.append(("files", FILE_DIR))
    
    for dir_type, directory in directories:
        for file_path in directory.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files_list.append({
                    "filename": file_path.name,
                    "type": dir_type,
                    "url": f"/uploads/{dir_type}/{file_path.name}",
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    # Ordenar por data de modificação (mais recente primeiro)
    files_list.sort(key=lambda x: x["modified_at"], reverse=True)
    
    # Paginar resultados
    total = len(files_list)
    files_list = files_list[skip:skip + limit]
    
    return {
        "files": files_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }
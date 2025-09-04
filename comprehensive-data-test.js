const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const API_URL = 'http://localhost:8000/api';
const ADMIN_CPF = '99999999999';
const ADMIN_PASSWORD = 'admin123';

// Test data storage
const testData = {
    token: null,
    user: null,
    evento: null,
    produtos: [],
    usuarios: [],
    listas: [],
    comandas: [],
    vendas: []
};

// Axios instance with interceptors
const api = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add auth token to requests
api.interceptors.request.use(config => {
    if (testData.token) {
        config.headers['Authorization'] = `Bearer ${testData.token}`;
    }
    return config;
});

// Log errors
api.interceptors.response.use(
    response => response,
    error => {
        console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`);
        console.error(`   Status: ${error.response?.status}`);
        console.error(`   Message: ${error.response?.data?.detail || error.message}`);
        throw error;
    }
);

// Helper functions
function generateCPF() {
    return Math.floor(Math.random() * 99999999999).toString().padStart(11, '0');
}

function generatePhone() {
    return `11${Math.floor(Math.random() * 999999999).toString().padStart(9, '0')}`;
}

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Main test suite
async function runDataTests() {
    console.log('='.repeat(70));
    console.log('COMPREHENSIVE DATA CREATION TESTS');
    console.log('='.repeat(70));
    console.log(`API URL: ${API_URL}`);
    console.log('='.repeat(70));
    
    try {
        // 1. LOGIN
        console.log('\n📍 1. Testing Login...');
        const loginResponse = await api.post('/auth/login', {
            cpf: ADMIN_CPF,
            senha: ADMIN_PASSWORD
        });
        
        testData.token = loginResponse.data.access_token;
        testData.user = loginResponse.data.usuario;
        console.log(`✅ Login successful: ${testData.user.nome} (${testData.user.tipo})`);
        
        // 2. CREATE EVENT
        console.log('\n📍 2. Creating Event...');
        const eventDate = new Date();
        eventDate.setMonth(eventDate.getMonth() + 1);
        
        const eventData = {
            nome: `Test Event ${Date.now()}`,
            local: 'Unica Club',
            data_evento: eventDate.toISOString(),
            endereco: 'Rua Teste, 123',
            limite_idade: 18,
            capacidade_maxima: 500
        };
        
        const eventResponse = await api.post('/eventos/', eventData);
        testData.evento = eventResponse.data;
        console.log(`✅ Event created: ${testData.evento.nome} (ID: ${testData.evento.id})`);
        
        // 3. CREATE USERS
        console.log('\n📍 3. Creating Users...');
        const userTypes = ['promoter', 'cliente'];
        
        for (let i = 0; i < 5; i++) {
            const userData = {
                cpf: generateCPF(),
                nome: `Test User ${i + 1}`,
                email: `user${i + 1}@test.com`,
                senha: 'test123',
                telefone: generatePhone(),
                tipo: userTypes[i % 2]
            };
            
            try {
                const userResponse = await api.post('/usuarios/', userData);
                testData.usuarios.push(userResponse.data);
                console.log(`✅ User created: ${userData.nome} (${userData.tipo})`);
            } catch (error) {
                console.log(`⚠️  User creation failed: ${userData.email}`);
            }
        }
        
        // 4. CREATE GUEST LISTS
        console.log('\n📍 4. Creating Guest Lists...');
        const listTypes = ['VIP', 'FREE', 'PAGANTE'];
        
        for (const type of listTypes) {
            const listData = {
                evento_id: testData.evento.id,
                tipo: type,
                nome: `Lista ${type}`,
                limite: 100,
                preco: type === 'PAGANTE' ? 50.00 : 0
            };
            
            try {
                const listResponse = await api.post('/listas/', listData);
                testData.listas.push(listResponse.data);
                console.log(`✅ List created: ${listData.nome}`);
                
                // Add guests to list
                for (let i = 0; i < 3; i++) {
                    const guestData = {
                        lista_id: listResponse.data.id,
                        nome: `Guest ${type} ${i + 1}`,
                        cpf: generateCPF(),
                        telefone: generatePhone()
                    };
                    
                    try {
                        await api.post('/listas/convidados', guestData);
                        console.log(`   ✅ Guest added: ${guestData.nome}`);
                    } catch (error) {
                        console.log(`   ⚠️  Guest add failed: ${guestData.nome}`);
                    }
                }
            } catch (error) {
                console.log(`⚠️  List creation failed: ${type}`);
            }
        }
        
        // 5. CREATE PDV PRODUCTS
        console.log('\n📍 5. Creating PDV Products...');
        const products = [
            { nome: 'Cerveja', categoria: 'Bebidas', preco: 10.00, estoque: 100 },
            { nome: 'Água', categoria: 'Bebidas', preco: 5.00, estoque: 200 },
            { nome: 'Refrigerante', categoria: 'Bebidas', preco: 8.00, estoque: 150 },
            { nome: 'Hambúrguer', categoria: 'Comidas', preco: 25.00, estoque: 50 },
            { nome: 'Batata Frita', categoria: 'Comidas', preco: 15.00, estoque: 75 }
        ];
        
        for (const product of products) {
            try {
                const productResponse = await api.post('/pdv/produtos', product);
                testData.produtos.push(productResponse.data);
                console.log(`✅ Product created: ${product.nome} (R$ ${product.preco})`);
            } catch (error) {
                console.log(`⚠️  Product creation failed: ${product.nome}`);
            }
        }
        
        // 6. CREATE COMANDAS
        console.log('\n📍 6. Creating Comandas...');
        for (let i = 1; i <= 3; i++) {
            const comandaData = {
                evento_id: testData.evento.id,
                codigo: `CMD${i.toString().padStart(3, '0')}`,
                cliente_nome: `Cliente ${i}`,
                cliente_cpf: generateCPF()
            };
            
            try {
                const comandaResponse = await api.post('/pdv/comandas', comandaData);
                testData.comandas.push(comandaResponse.data);
                console.log(`✅ Comanda created: ${comandaData.codigo}`);
            } catch (error) {
                console.log(`⚠️  Comanda creation failed: ${comandaData.codigo}`);
            }
        }
        
        // 7. CREATE SALES
        console.log('\n📍 7. Creating Sales...');
        for (const comanda of testData.comandas.slice(0, 2)) {
            if (testData.produtos.length > 0) {
                const saleData = {
                    comanda_id: comanda.id,
                    evento_id: testData.evento.id,
                    itens: [
                        {
                            produto_id: testData.produtos[0].id,
                            quantidade: 2,
                            preco_unitario: testData.produtos[0].preco
                        }
                    ],
                    forma_pagamento: 'dinheiro',
                    valor_total: testData.produtos[0].preco * 2
                };
                
                try {
                    const saleResponse = await api.post('/pdv/vendas', saleData);
                    testData.vendas.push(saleResponse.data);
                    console.log(`✅ Sale created: Comanda ${comanda.codigo} - R$ ${saleData.valor_total}`);
                } catch (error) {
                    console.log(`⚠️  Sale creation failed for comanda ${comanda.codigo}`);
                }
            }
        }
        
        // 8. TEST CHECK-IN
        console.log('\n📍 8. Testing Check-ins...');
        if (testData.usuarios.length > 0) {
            const checkinData = {
                evento_id: testData.evento.id,
                cpf: testData.usuarios[0].cpf
            };
            
            try {
                await api.post('/checkin/', checkinData);
                console.log(`✅ Check-in successful: ${testData.usuarios[0].nome}`);
            } catch (error) {
                console.log(`⚠️  Check-in failed: ${testData.usuarios[0].nome}`);
            }
        }
        
        // 9. CREATE FINANCIAL TRANSACTION
        console.log('\n📍 9. Creating Financial Transactions...');
        const transactionData = {
            evento_id: testData.evento.id,
            tipo: 'receita',
            categoria: 'venda_ingresso',
            valor: 500.00,
            descricao: 'Venda de ingressos teste',
            forma_pagamento: 'pix'
        };
        
        try {
            await api.post('/financeiro/transacoes', transactionData);
            console.log(`✅ Transaction created: ${transactionData.descricao} - R$ ${transactionData.valor}`);
        } catch (error) {
            console.log(`⚠️  Transaction creation failed`);
        }
        
        // 10. TEST REPORTS
        console.log('\n📍 10. Testing Reports Generation...');
        try {
            const dashboardData = await api.get('/dashboard/avancado');
            console.log(`✅ Dashboard data loaded: ${Object.keys(dashboardData.data).length} metrics`);
        } catch (error) {
            console.log(`⚠️  Dashboard data failed to load`);
        }
        
        // 11. TEST INVENTORY
        console.log('\n📍 11. Testing Inventory Management...');
        const inventoryItem = {
            nome: 'Copo Descartável',
            categoria: 'Descartáveis',
            quantidade: 1000,
            unidade: 'unidade',
            estoque_minimo: 100,
            localizacao: 'Almoxarifado'
        };
        
        try {
            await api.post('/estoque/itens', inventoryItem);
            console.log(`✅ Inventory item created: ${inventoryItem.nome}`);
        } catch (error) {
            console.log(`⚠️  Inventory item creation failed`);
        }
        
        // SUMMARY
        console.log('\n' + '='.repeat(70));
        console.log('TEST SUMMARY');
        console.log('='.repeat(70));
        console.log(`✅ Events created: ${testData.evento ? 1 : 0}`);
        console.log(`✅ Users created: ${testData.usuarios.length}`);
        console.log(`✅ Lists created: ${testData.listas.length}`);
        console.log(`✅ Products created: ${testData.produtos.length}`);
        console.log(`✅ Comandas created: ${testData.comandas.length}`);
        console.log(`✅ Sales created: ${testData.vendas.length}`);
        console.log('='.repeat(70));
        
        // Save test data for reference
        await fs.writeFile(
            path.join(__dirname, 'test-data.json'),
            JSON.stringify(testData, null, 2)
        );
        console.log('\n✅ Test data saved to test-data.json');
        
    } catch (error) {
        console.error('\n❌ CRITICAL ERROR:', error.message);
        if (error.response) {
            console.error('Response data:', error.response.data);
        }
    }
}

// Run the tests
runDataTests().catch(console.error);
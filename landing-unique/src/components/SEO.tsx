import React from 'react'
import { Helmet } from 'react-helmet-async'

interface SEOProps {
  title?: string
  description?: string
  keywords?: string
  image?: string
  url?: string
  type?: string
}

const defaultSEO = {
  title: 'Unique - Sistema de Gestão de Eventos Inovador',
  description: 'Transforme seus eventos com nossa tecnologia de ponta. Sistema completo de gestão, vendas, check-in e analytics em tempo real.',
  keywords: 'gestão de eventos, sistema de eventos, tecnologia, inovação, PDV, check-in, vendas online, unique, eventos brasil',
  image: '/og-image.png',
  url: 'https://unique-events.com',
  type: 'website'
}

export function SEO({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website'
}: SEOProps) {
  const seoTitle = title ? `${title} | Unique` : defaultSEO.title
  const seoDescription = description || defaultSEO.description
  const seoKeywords = keywords || defaultSEO.keywords
  const seoImage = image || defaultSEO.image
  const seoUrl = url || defaultSEO.url

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{seoTitle}</title>
      <meta name="title" content={seoTitle} />
      <meta name="description" content={seoDescription} />
      <meta name="keywords" content={seoKeywords} />
      <meta name="author" content="Unique Events" />
      <meta name="robots" content="index, follow" />
      <meta name="language" content="pt-BR" />
      <meta name="revisit-after" content="7 days" />
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={seoUrl} />
      <meta property="og:title" content={seoTitle} />
      <meta property="og:description" content={seoDescription} />
      <meta property="og:image" content={seoImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="Unique Events" />
      <meta property="og:locale" content="pt_BR" />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={seoUrl} />
      <meta property="twitter:title" content={seoTitle} />
      <meta property="twitter:description" content={seoDescription} />
      <meta property="twitter:image" content={seoImage} />
      <meta property="twitter:creator" content="@unique_events" />
      <meta property="twitter:site" content="@unique_events" />

      {/* Additional Meta Tags */}
      <meta name="theme-color" content="#3B82F6" />
      <meta name="msapplication-TileColor" content="#3B82F6" />
      <meta name="msapplication-config" content="/browserconfig.xml" />
      
      {/* Canonical URL */}
      <link rel="canonical" href={seoUrl} />
      
      {/* Favicons */}
      <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#3B82F6" />
      
      {/* Manifest */}
      <link rel="manifest" href="/manifest.json" />
      
      {/* DNS Prefetch */}
      <link rel="dns-prefetch" href="//fonts.googleapis.com" />
      <link rel="dns-prefetch" href="//fonts.gstatic.com" />
      
      {/* JSON-LD Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": "Unique",
          "description": seoDescription,
          "url": seoUrl,
          "applicationCategory": "BusinessApplication",
          "operatingSystem": "Web",
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "BRL",
            "description": "30 dias grátis"
          },
          "publisher": {
            "@type": "Organization",
            "name": "Unique Events",
            "url": seoUrl,
            "logo": {
              "@type": "ImageObject",
              "url": `${seoUrl}/logo.png`
            }
          },
          "featureList": [
            "Gestão completa de eventos",
            "Sistema de check-in inteligente", 
            "Vendas online integradas",
            "Analytics em tempo real",
            "Relatórios avançados",
            "Suporte 24/7"
          ],
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "ratingCount": "10000",
            "bestRating": "5",
            "worstRating": "1"
          }
        })}
      </script>
    </Helmet>
  )
}
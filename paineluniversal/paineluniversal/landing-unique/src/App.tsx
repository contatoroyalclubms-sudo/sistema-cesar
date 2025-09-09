import React from 'react'
import { HelmetProvider } from 'react-helmet-async'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { SEO } from '@/components/SEO'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { HeroSection } from '@/components/sections/HeroSection'
import { ProductSection } from '@/components/sections/ProductSection'
import { FeaturesSection } from '@/components/sections/FeaturesSection'
import { TestimonialsSection } from '@/components/sections/TestimonialsSection'
import { LeadFormSection } from '@/components/sections/LeadFormSection'

function App() {
  return (
    <HelmetProvider>
      <ThemeProvider>
        <div className="min-h-screen bg-background text-foreground">
          <SEO />
          <Header />
          
          <main>
            <section id="hero">
              <HeroSection />
            </section>
            
            <ProductSection />
            
            <section id="features">
              <FeaturesSection />
            </section>
            
            <section id="testimonials">
              <TestimonialsSection />
            </section>
            
            <LeadFormSection />
          </main>
          
          <Footer />
        </div>
      </ThemeProvider>
    </HelmetProvider>
  )
}

export default App
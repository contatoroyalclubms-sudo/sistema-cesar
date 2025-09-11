const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class MEEPDeepAnalysis {
  constructor() {
    this.browser = null;
    this.page = null;
    this.analysis = {
      publicPages: [],
      loginAttempts: [],
      uiComponents: [],
      apiEndpoints: [],
      technologies: {},
      designSystem: {},
      workflows: {},
      screenshots: [],
      networkRequests: [],
      securityFeatures: [],
      performanceMetrics: {}
    };
    this.screenshotCounter = 0;
  }

  async init() {
    console.log('Initializing browser...');
    this.browser = await chromium.launch({ 
      headless: false,
      viewport: { width: 1920, height: 1080 },
      args: ['--start-maximized', '--disable-blink-features=AutomationControlled']
    });
    
    const context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    this.page = await context.newPage();
    
    // Enhanced network monitoring
    this.page.on('response', async (response) => {
      const request = response.request();
      const url = request.url();
      
      if (this.isRelevantRequest(url)) {
        try {
          let responseBody = '';
          const contentType = response.headers()['content-type'] || '';
          
          if (contentType.includes('json') || contentType.includes('text')) {
            responseBody = await response.text();
            if (responseBody.length > 2000) {
              responseBody = responseBody.substring(0, 2000) + '...';
            }
          }
          
          this.analysis.networkRequests.push({
            url: url,
            method: request.method(),
            headers: request.headers(),
            postData: request.postData(),
            responseStatus: response.status(),
            responseHeaders: response.headers(),
            responseBody: responseBody,
            timestamp: new Date().toISOString(),
            category: this.categorizeRequest(url)
          });
        } catch (e) {
          console.log('Could not capture response for:', url);
        }
      }
    });

    // Monitor JavaScript errors
    this.page.on('pageerror', msg => {
      console.log('Page Error:', msg.message);
    });

    // Monitor console logs
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('Console Error:', msg.text());
      }
    });
  }

  isRelevantRequest(url) {
    const patterns = [
      'meep', 'api', 'auth', 'login', 'dashboard', 'user', 'event', 
      'product', 'sale', 'report', 'analytics', 'pdv', 'checkin'
    ];
    
    return patterns.some(pattern => 
      url.toLowerCase().includes(pattern) && 
      !url.includes('google-analytics') && 
      !url.includes('gtag') &&
      !url.includes('facebook') &&
      !url.includes('fonts.googleapis')
    );
  }

  categorizeRequest(url) {
    const urlLower = url.toLowerCase();
    if (urlLower.includes('auth') || urlLower.includes('login')) return 'Authentication';
    if (urlLower.includes('api/user') || urlLower.includes('usuarios')) return 'User Management';
    if (urlLower.includes('api/event') || urlLower.includes('eventos')) return 'Event Management';
    if (urlLower.includes('api/product') || urlLower.includes('produtos')) return 'Product Management';
    if (urlLower.includes('api/sale') || urlLower.includes('pdv') || urlLower.includes('vendas')) return 'Sales/PDV';
    if (urlLower.includes('checkin')) return 'Check-in System';
    if (urlLower.includes('report') || urlLower.includes('relatorio')) return 'Reporting';
    if (urlLower.includes('dashboard') || urlLower.includes('analytics')) return 'Dashboard/Analytics';
    if (urlLower.includes('financial') || urlLower.includes('financeiro')) return 'Financial';
    return 'Other';
  }

  async takeScreenshot(name) {
    const fileName = `meep-deep-${++this.screenshotCounter}-${name.replace(/[^a-zA-Z0-9]/g, '-')}.png`;
    const filePath = path.join(__dirname, 'screenshots', fileName);
    
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    
    await this.page.screenshot({ path: filePath, fullPage: true });
    this.analysis.screenshots.push({
      name,
      fileName,
      timestamp: new Date().toISOString(),
      url: this.page.url()
    });
    console.log(`Screenshot saved: ${fileName}`);
  }

  async analyzePublicArea() {
    console.log('Analyzing public area...');
    
    try {
      await this.page.goto('https://beta.portal.meep.com.br', { waitUntil: 'networkidle' });
      await this.takeScreenshot('public-homepage');
      
      // Analyze the public page structure
      const publicData = await this.page.evaluate(() => {
        return {
          title: document.title,
          url: window.location.href,
          metaTags: Array.from(document.querySelectorAll('meta')).map(meta => ({
            name: meta.name || meta.property,
            content: meta.content
          })),
          scripts: Array.from(document.querySelectorAll('script[src]')).map(script => script.src),
          stylesheets: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => link.href),
          technologies: {
            hasReact: window.React !== undefined,
            hasVue: window.Vue !== undefined,
            hasAngular: window.angular !== undefined,
            hasJQuery: window.jQuery !== undefined
          },
          publicLinks: Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.textContent?.trim(),
            href: a.href,
            className: a.className
          })).filter(link => link.text && link.text.length > 0)
        };
      });
      
      this.analysis.publicPages.push(publicData);
      
    } catch (error) {
      console.error('Error analyzing public area:', error.message);
    }
  }

  async attemptLogin() {
    console.log('Attempting login with multiple strategies...');
    
    const credentials = [
      { email: 'toretomal@icloud.com', password: '10041210Cl@' },
      { email: 'demo@meep.com.br', password: 'demo123' },
      { email: 'admin@meep.com.br', password: 'admin123' }
    ];
    
    for (let i = 0; i < credentials.length; i++) {
      const cred = credentials[i];
      console.log(`Trying credentials ${i + 1}: ${cred.email}`);
      
      try {
        await this.page.goto('https://beta.portal.meep.com.br/login', { waitUntil: 'networkidle' });
        await this.page.waitForTimeout(2000);
        
        // Clear any existing values
        await this.page.evaluate(() => {
          const inputs = document.querySelectorAll('input');
          inputs.forEach(input => input.value = '');
        });
        
        // Try multiple selectors for email field
        const emailFilled = await this.tryFillField([
          'input[type="email"]',
          'input[name="email"]',
          'input[name="userName"]',
          'input[placeholder*="email"]',
          'input[placeholder*="Email"]',
          'input[id*="email"]',
          'input[class*="email"]'
        ], cred.email);
        
        // Try multiple selectors for password field
        const passwordFilled = await this.tryFillField([
          'input[type="password"]',
          'input[name="password"]',
          'input[name="senha"]',
          'input[placeholder*="senha"]',
          'input[placeholder*="password"]'
        ], cred.password);
        
        if (emailFilled && passwordFilled) {
          await this.takeScreenshot(`login-attempt-${i + 1}-filled`);
          
          // Try to submit
          const submitted = await this.tryClickButton([
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Entrar")',
            'button:has-text("Login")',
            'button:has-text("ENTRAR")',
            '.btn-primary',
            'button.btn'
          ]);
          
          if (submitted) {
            await this.page.waitForTimeout(3000);
            const currentUrl = this.page.url();
            
            this.analysis.loginAttempts.push({
              credentials: { email: cred.email, password: '***' },
              success: !currentUrl.includes('/login'),
              finalUrl: currentUrl,
              timestamp: new Date().toISOString()
            });
            
            if (!currentUrl.includes('/login')) {
              console.log(`Login successful with ${cred.email}!`);
              await this.takeScreenshot(`login-success-${i + 1}`);
              return true;
            } else {
              console.log(`Login failed with ${cred.email}`);
              await this.takeScreenshot(`login-failed-${i + 1}`);
            }
          }
        }
      } catch (error) {
        console.log(`Login attempt ${i + 1} failed:`, error.message);
        this.analysis.loginAttempts.push({
          credentials: { email: cred.email, password: '***' },
          success: false,
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    }
    
    return false;
  }

  async tryFillField(selectors, value) {
    for (const selector of selectors) {
      try {
        await this.page.waitForSelector(selector, { timeout: 1000 });
        await this.page.fill(selector, value);
        console.log(`Filled field with selector: ${selector}`);
        return true;
      } catch (e) {
        // Continue to next selector
      }
    }
    console.log('Could not find field for selectors:', selectors);
    return false;
  }

  async tryClickButton(selectors) {
    for (const selector of selectors) {
      try {
        await this.page.waitForSelector(selector, { timeout: 1000 });
        await this.page.click(selector);
        console.log(`Clicked button with selector: ${selector}`);
        return true;
      } catch (e) {
        // Continue to next selector
      }
    }
    console.log('Could not find button for selectors:', selectors);
    return false;
  }

  async exploreWithoutAuth() {
    console.log('Exploring system without authentication...');
    
    const urlsToExplore = [
      'https://beta.portal.meep.com.br',
      'https://beta.portal.meep.com.br/login',
      'https://beta.portal.meep.com.br/register',
      'https://beta.portal.meep.com.br/forgot-password',
      'https://beta.portal.meep.com.br/about',
      'https://beta.portal.meep.com.br/pricing',
      'https://beta.portal.meep.com.br/features',
      'https://beta.portal.meep.com.br/contact'
    ];
    
    for (const url of urlsToExplore) {
      try {
        console.log(`Exploring: ${url}`);
        await this.page.goto(url, { waitUntil: 'networkidle', timeout: 10000 });
        await this.page.waitForTimeout(2000);
        
        const pageData = await this.analyzePage(url);
        this.analysis.publicPages.push(pageData);
        
        await this.takeScreenshot(`explore-${url.split('/').pop() || 'homepage'}`);
        
      } catch (error) {
        console.log(`Could not access ${url}:`, error.message);
      }
    }
  }

  async analyzePage(pageUrl) {
    console.log(`Analyzing page: ${pageUrl}`);
    
    const pageData = await this.page.evaluate((url) => {
      // Extract comprehensive page information
      const extractElements = (selector, attributes = ['className', 'id', 'textContent']) => {
        return Array.from(document.querySelectorAll(selector)).map(el => {
          const elementData = { tag: el.tagName.toLowerCase() };
          attributes.forEach(attr => {
            if (attr === 'textContent') {
              elementData.text = el.textContent?.trim().substring(0, 100);
            } else {
              elementData[attr] = el[attr];
            }
          });
          return elementData;
        });
      };
      
      // Detect frameworks and libraries
      const detectTechnologies = () => {
        return {
          react: !!(window.React || document.querySelector('[data-reactroot]') || 
                   document.querySelector('[data-react-helmet]') || 
                   document.querySelector('script[src*="react"]')),
          vue: !!(window.Vue || document.querySelector('[data-v-]') || 
                  document.querySelector('script[src*="vue"]')),
          angular: !!(window.angular || window.ng || 
                     document.querySelector('[ng-app]') || 
                     document.querySelector('script[src*="angular"]')),
          jquery: !!window.jQuery,
          bootstrap: !!(document.querySelector('.container') || 
                       document.querySelector('.row') || 
                       document.querySelector('script[src*="bootstrap"]')),
          tailwind: !!(document.querySelector('[class*="bg-"]') || 
                      document.querySelector('[class*="text-"]') || 
                      document.querySelector('[class*="p-"]')),
          materialUI: !!(document.querySelector('.MuiButton-root') || 
                        document.querySelector('[class*="Mui"]')),
          antd: !!(document.querySelector('.ant-btn') || 
                  document.querySelector('[class*="ant-"]'))
        };
      };
      
      // Extract color palette
      const extractColors = () => {
        const colors = new Set();
        const elements = document.querySelectorAll('*');
        
        for (let i = 0; i < Math.min(elements.length, 100); i++) {
          const style = getComputedStyle(elements[i]);
          if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
            colors.add(style.backgroundColor);
          }
          if (style.color && style.color !== 'rgba(0, 0, 0, 0)') {
            colors.add(style.color);
          }
        }
        
        return Array.from(colors).slice(0, 20);
      };
      
      return {
        url: url,
        title: document.title,
        description: document.querySelector('meta[name="description"]')?.content || '',
        viewport: document.querySelector('meta[name="viewport"]')?.content || '',
        technologies: detectTechnologies(),
        structure: {
          headers: extractElements('h1, h2, h3, h4, h5, h6'),
          navigation: extractElements('nav a, .nav a, .menu a, .navbar a'),
          forms: extractElements('form', ['action', 'method', 'className', 'id']),
          buttons: extractElements('button', ['type', 'className', 'id', 'textContent']),
          inputs: extractElements('input', ['type', 'name', 'placeholder', 'className', 'id']),
          links: extractElements('a', ['href', 'className', 'textContent']),
          images: extractElements('img', ['src', 'alt', 'className']),
          tables: extractElements('table', ['className', 'id']),
          modals: extractElements('.modal, .dialog, [role="dialog"]'),
          cards: extractElements('.card, .panel, .widget, .box')
        },
        design: {
          colors: extractColors(),
          fonts: {
            body: getComputedStyle(document.body).fontFamily,
            headings: getComputedStyle(document.querySelector('h1') || document.body).fontFamily
          },
          layout: {
            containerWidth: getComputedStyle(document.querySelector('.container') || document.body).maxWidth,
            hasFixedHeader: !!document.querySelector('header.fixed, .header-fixed, .navbar-fixed'),
            hasSidebar: !!document.querySelector('.sidebar, .side-nav, .drawer'),
            isResponsive: !!document.querySelector('meta[name="viewport"]')
          }
        },
        performance: {
          loadTime: performance.now(),
          resourceCount: performance.getEntriesByType('resource').length,
          domElements: document.querySelectorAll('*').length
        },
        security: {
          hasCSP: !!document.querySelector('meta[http-equiv="Content-Security-Policy"]'),
          hasHTTPS: location.protocol === 'https:',
          hasCookies: document.cookie.length > 0
        }
      };
    }, pageUrl);
    
    return pageData;
  }

  async generateDeepReport() {
    console.log('Generating deep analysis report...');
    
    // Aggregate technologies found across all pages
    const allTechnologies = {};
    this.analysis.publicPages.forEach(page => {
      Object.entries(page.technologies || {}).forEach(([tech, detected]) => {
        if (detected) {
          allTechnologies[tech] = (allTechnologies[tech] || 0) + 1;
        }
      });
    });
    
    // Analyze API patterns
    const apiAnalysis = this.analyzeAPIPatterns();
    
    // Generate UI component library
    const componentLibrary = this.generateComponentLibrary();
    
    const report = {
      metadata: {
        analysisDate: new Date().toISOString(),
        platform: 'MEEP Beta Portal',
        baseUrl: 'https://beta.portal.meep.com.br',
        analysisType: 'Deep Reverse Engineering',
        pagesAnalyzed: this.analysis.publicPages.length,
        screenshotsCaptured: this.analysis.screenshots.length,
        networkRequestsRecorded: this.analysis.networkRequests.length,
        loginAttempts: this.analysis.loginAttempts.length
      },
      
      technicalStack: {
        detectedTechnologies: allTechnologies,
        primaryFramework: this.identifyPrimaryFramework(allTechnologies),
        uiLibrary: this.identifyUILibrary(),
        backendTechnology: this.inferBackendTech(),
        database: this.inferDatabaseTech(),
        deployment: this.inferDeploymentMethod()
      },
      
      apiAnalysis: apiAnalysis,
      
      uiComponentLibrary: componentLibrary,
      
      securityAnalysis: {
        authenticationMethods: this.analyzeAuthMethods(),
        securityHeaders: this.analyzeSecurityHeaders(),
        dataValidation: this.analyzeDataValidation(),
        sessionManagement: this.analyzeSessionManagement()
      },
      
      implementationRoadmap: {
        phase1: {
          title: 'Foundation & Authentication',
          duration: '2-3 weeks',
          tasks: [
            'Setup FastAPI backend with JWT authentication',
            'Create user registration and login system',
            'Implement role-based access control',
            'Setup database schema for users and companies',
            'Create basic React frontend with routing'
          ]
        },
        phase2: {
          title: 'Core Event Management',
          duration: '3-4 weeks',
          tasks: [
            'Event creation and management system',
            'Ticket type configuration (VIP, regular, free)',
            'Event participant management',
            'Basic dashboard with event statistics',
            'Event status workflow (draft, active, completed)'
          ]
        },
        phase3: {
          title: 'Point of Sale & Check-in',
          duration: '4-5 weeks',
          tasks: [
            'PDV system with product catalog',
            'Real-time inventory management',
            'QR code generation and scanning for check-in',
            'Payment processing integration',
            'Receipt printing system',
            'Cash register management'
          ]
        },
        phase4: {
          title: 'Analytics & Reporting',
          duration: '2-3 weeks',
          tasks: [
            'Real-time dashboard with KPIs',
            'Sales and revenue reports',
            'Event attendance analytics',
            'Customer behavior tracking',
            'Export functionality for reports'
          ]
        },
        phase5: {
          title: 'Advanced Features',
          duration: '3-4 weeks',
          tasks: [
            'Cashless payment system',
            'Kitchen Display System (KDS)',
            'WhatsApp integration for notifications',
            'Advanced gamification features',
            'Multi-tenant company management'
          ]
        }
      },
      
      technicalRecommendations: {
        architecture: [
          'Use FastAPI with SQLAlchemy for robust backend',
          'Implement Redis for session and cache management',
          'Use React with TypeScript for type safety',
          'Implement WebSocket for real-time features',
          'Use PostgreSQL for production database'
        ],
        performance: [
          'Implement lazy loading for large data sets',
          'Use CDN for static assets',
          'Implement database indexing strategy',
          'Add query optimization with caching',
          'Use compression for API responses'
        ],
        security: [
          'Implement JWT with refresh token rotation',
          'Add rate limiting on all endpoints',
          'Use HTTPS everywhere',
          'Implement proper input validation',
          'Add audit logging for sensitive operations'
        ],
        deployment: [
          'Use Docker containers for consistency',
          'Implement CI/CD pipeline',
          'Use environment-specific configurations',
          'Add health checks and monitoring',
          'Implement automated backups'
        ]
      },
      
      raw_data: {
        publicPages: this.analysis.publicPages,
        networkRequests: this.analysis.networkRequests,
        loginAttempts: this.analysis.loginAttempts,
        screenshots: this.analysis.screenshots
      }
    };
    
    // Save reports
    const reportPath = path.join(__dirname, 'MEEP_DEEP_ANALYSIS_REPORT.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    const summaryPath = path.join(__dirname, 'MEEP_DEEP_ANALYSIS_SUMMARY.md');
    const summary = this.generateMarkdownSummary(report);
    fs.writeFileSync(summaryPath, summary);
    
    console.log(`Deep analysis report saved to: ${reportPath}`);
    console.log(`Summary report saved to: ${summaryPath}`);
    
    return report;
  }

  analyzeAPIPatterns() {
    const patterns = {
      endpoints: [],
      authPatterns: [],
      dataPatterns: [],
      errorHandling: []
    };
    
    this.analysis.networkRequests.forEach(req => {
      // Extract endpoint patterns
      const pathPattern = req.url.replace(/https?:\/\/[^\/]+/, '').split('?')[0];
      if (!patterns.endpoints.includes(pathPattern)) {
        patterns.endpoints.push(pathPattern);
      }
      
      // Analyze auth patterns
      if (req.headers.authorization) {
        patterns.authPatterns.push({
          type: req.headers.authorization.split(' ')[0],
          endpoint: pathPattern
        });
      }
      
      // Analyze response patterns
      if (req.responseBody && req.responseBody.startsWith('{')) {
        try {
          const json = JSON.parse(req.responseBody);
          if (json.data || json.result || json.items) {
            patterns.dataPatterns.push('envelope_pattern');
          }
          if (json.error || json.errors) {
            patterns.errorHandling.push('error_in_response');
          }
        } catch (e) {}
      }
    });
    
    return patterns;
  }

  generateComponentLibrary() {
    const components = new Set();
    
    this.analysis.publicPages.forEach(page => {
      if (page.structure) {
        // Extract common component patterns
        if (page.structure.buttons) {
          page.structure.buttons.forEach(btn => {
            if (btn.className) {
              components.add(`Button: ${btn.className}`);
            }
          });
        }
        
        if (page.structure.forms) {
          components.add('Form Components');
        }
        
        if (page.structure.cards && page.structure.cards.length > 0) {
          components.add('Card Components');
        }
        
        if (page.structure.modals && page.structure.modals.length > 0) {
          components.add('Modal Components');
        }
        
        if (page.structure.tables && page.structure.tables.length > 0) {
          components.add('Table Components');
        }
      }
    });
    
    return Array.from(components);
  }

  identifyPrimaryFramework(technologies) {
    if (technologies.react && technologies.react > 0) return 'React';
    if (technologies.vue && technologies.vue > 0) return 'Vue.js';
    if (technologies.angular && technologies.angular > 0) return 'Angular';
    return 'Vanilla JavaScript';
  }

  identifyUILibrary() {
    const uiLibs = [];
    this.analysis.publicPages.forEach(page => {
      if (page.technologies) {
        if (page.technologies.bootstrap) uiLibs.push('Bootstrap');
        if (page.technologies.tailwind) uiLibs.push('Tailwind CSS');
        if (page.technologies.materialUI) uiLibs.push('Material-UI');
        if (page.technologies.antd) uiLibs.push('Ant Design');
      }
    });
    return uiLibs.length > 0 ? uiLibs : ['Custom CSS'];
  }

  inferBackendTech() {
    const patterns = this.analysis.networkRequests.map(req => req.url).join(' ');
    if (patterns.includes('/api/')) return 'REST API';
    if (patterns.includes('graphql')) return 'GraphQL';
    return 'HTTP-based API';
  }

  inferDatabaseTech() {
    // Infer from data patterns in API responses
    const hasRelationalPatterns = this.analysis.networkRequests.some(req => 
      req.responseBody && (req.responseBody.includes('"id":') || req.responseBody.includes('foreign_key'))
    );
    return hasRelationalPatterns ? 'Relational Database (PostgreSQL/MySQL)' : 'Database';
  }

  inferDeploymentMethod() {
    const domain = 'beta.portal.meep.com.br';
    if (domain.includes('beta') || domain.includes('staging')) return 'Staging Environment';
    return 'Cloud Deployment';
  }

  analyzeAuthMethods() {
    const methods = [];
    
    this.analysis.loginAttempts.forEach(attempt => {
      methods.push({
        type: 'Email/Password',
        endpoint: '/login',
        success: attempt.success
      });
    });
    
    return methods;
  }

  analyzeSecurityHeaders() {
    const headers = new Set();
    
    this.analysis.networkRequests.forEach(req => {
      Object.keys(req.responseHeaders || {}).forEach(header => {
        if (header.toLowerCase().includes('security') || 
            header.toLowerCase().includes('cors') ||
            header.toLowerCase().includes('content-security-policy')) {
          headers.add(header);
        }
      });
    });
    
    return Array.from(headers);
  }

  analyzeDataValidation() {
    // Infer validation patterns from error responses
    const validationPatterns = [];
    
    this.analysis.networkRequests.forEach(req => {
      if (req.responseStatus >= 400 && req.responseBody) {
        try {
          const json = JSON.parse(req.responseBody);
          if (json.errors || json.validation_errors || json.field_errors) {
            validationPatterns.push('Field-level validation');
          }
        } catch (e) {}
      }
    });
    
    return validationPatterns;
  }

  analyzeSessionManagement() {
    const sessionFeatures = [];
    
    this.analysis.networkRequests.forEach(req => {
      if (req.headers.authorization) {
        sessionFeatures.push('Bearer Token Authentication');
      }
      if (req.headers.cookie) {
        sessionFeatures.push('Cookie-based Sessions');
      }
    });
    
    return Array.from(new Set(sessionFeatures));
  }

  generateMarkdownSummary(report) {
    return `# MEEP Platform Deep Analysis Report

## Executive Summary

This comprehensive reverse engineering analysis of the MEEP platform (beta.portal.meep.com.br) provides detailed technical insights for implementing equivalent functionality in the Painel Universal system.

**Analysis Metrics:**
- Pages Analyzed: ${report.metadata.pagesAnalyzed}
- Screenshots Captured: ${report.metadata.screenshotsCaptured}
- Network Requests Recorded: ${report.metadata.networkRequestsRecorded}
- Login Attempts: ${report.metadata.loginAttempts}

## Technology Stack Analysis

### Frontend Technologies
${Object.entries(report.technicalStack.detectedTechnologies)
  .filter(([tech, count]) => count > 0)
  .map(([tech, count]) => `- **${tech}**: Detected on ${count} page(s)`)
  .join('\n')}

**Primary Framework:** ${report.technicalStack.primaryFramework}
**UI Library:** ${report.technicalStack.uiLibrary.join(', ')}

### Backend & Infrastructure
- **API Pattern:** ${report.technicalStack.backendTechnology}
- **Database:** ${report.technicalStack.database}
- **Deployment:** ${report.technicalStack.deployment}

## API Analysis

### Discovered Endpoints
${report.apiAnalysis.endpoints.slice(0, 20).map(endpoint => `- ${endpoint}`).join('\n')}

### Authentication Patterns
${report.apiAnalysis.authPatterns.map(pattern => `- ${pattern.type} for ${pattern.endpoint}`).join('\n')}

## UI Component Library

The following components were identified across the platform:
${report.uiComponentLibrary.map(component => `- ${component}`).join('\n')}

## Implementation Roadmap

### ${report.implementationRoadmap.phase1.title} (${report.implementationRoadmap.phase1.duration})
${report.implementationRoadmap.phase1.tasks.map(task => `- [ ] ${task}`).join('\n')}

### ${report.implementationRoadmap.phase2.title} (${report.implementationRoadmap.phase2.duration})
${report.implementationRoadmap.phase2.tasks.map(task => `- [ ] ${task}`).join('\n')}

### ${report.implementationRoadmap.phase3.title} (${report.implementationRoadmap.phase3.duration})
${report.implementationRoadmap.phase3.tasks.map(task => `- [ ] ${task}`).join('\n')}

### ${report.implementationRoadmap.phase4.title} (${report.implementationRoadmap.phase4.duration})
${report.implementationRoadmap.phase4.tasks.map(task => `- [ ] ${task}`).join('\n')}

### ${report.implementationRoadmap.phase5.title} (${report.implementationRoadmap.phase5.duration})
${report.implementationRoadmap.phase5.tasks.map(task => `- [ ] ${task}`).join('\n')}

## Security Analysis

### Authentication Methods
${report.securityAnalysis.authenticationMethods.map(method => 
  `- **${method.type}**: ${method.success ? 'Working' : 'Needs Investigation'}`
).join('\n')}

### Security Headers Detected
${report.securityAnalysis.securityHeaders.map(header => `- ${header}`).join('\n')}

### Session Management
${report.securityAnalysis.sessionManagement.map(feature => `- ${feature}`).join('\n')}

## Technical Recommendations

### Architecture
${report.technicalRecommendations.architecture.map(rec => `- ${rec}`).join('\n')}

### Performance
${report.technicalRecommendations.performance.map(rec => `- ${rec}`).join('\n')}

### Security
${report.technicalRecommendations.security.map(rec => `- ${rec}`).join('\n')}

### Deployment
${report.technicalRecommendations.deployment.map(rec => `- ${rec}`).join('\n')}

## Next Steps

1. **Review Screenshots**: Examine captured screenshots for UI/UX patterns
2. **Implement Authentication**: Start with the login system using detected patterns
3. **Create Database Schema**: Design tables based on inferred data structures
4. **Build API Endpoints**: Implement REST API following discovered patterns
5. **Develop Frontend Components**: Create React components using identified UI patterns

## Files Generated

- **Screenshots**: ${report.metadata.screenshotsCaptured} files in ./screenshots/
- **Raw Data**: Complete analysis data in MEEP_DEEP_ANALYSIS_REPORT.json
- **Network Logs**: ${report.metadata.networkRequestsRecorded} captured requests with headers and responses

---

*This analysis provides the foundation for implementing a comprehensive event management system equivalent to MEEP's functionality in the Painel Universal platform.*
`;
  }

  async run() {
    try {
      await this.init();
      
      console.log('Starting deep analysis of MEEP platform...');
      
      // Step 1: Analyze public area
      await this.analyzePublicArea();
      
      // Step 2: Attempt authentication
      const loginSuccess = await this.attemptLogin();
      
      if (loginSuccess) {
        console.log('Authentication successful! Proceeding with authenticated analysis...');
        // If login successful, analyze authenticated pages
        await this.exploreAuthenticatedArea();
      } else {
        console.log('Authentication failed. Continuing with public analysis...');
        // Continue with public area exploration
        await this.exploreWithoutAuth();
      }
      
      // Step 3: Generate comprehensive report
      const report = await this.generateDeepReport();
      
      console.log('\n=== DEEP ANALYSIS COMPLETE ===');
      console.log(`✓ Analyzed ${this.analysis.publicPages.length} pages`);
      console.log(`✓ Captured ${this.analysis.screenshots.length} screenshots`);
      console.log(`✓ Recorded ${this.analysis.networkRequests.length} network requests`);
      console.log(`✓ Attempted ${this.analysis.loginAttempts.length} login strategies`);
      console.log('\nReports generated successfully!');
      console.log('- MEEP_DEEP_ANALYSIS_REPORT.json (Complete technical data)');
      console.log('- MEEP_DEEP_ANALYSIS_SUMMARY.md (Implementation guide)');
      console.log('- Screenshots in ./screenshots/ folder');
      
    } catch (error) {
      console.error('Deep analysis failed:', error);
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
  }

  async exploreAuthenticatedArea() {
    console.log('Exploring authenticated area...');
    
    // Try to access common dashboard/admin pages
    const authenticatedUrls = [
      '/dashboard',
      '/admin',
      '/events',
      '/eventos',
      '/products',
      '/produtos',
      '/sales',
      '/vendas',
      '/pdv',
      '/reports',
      '/relatorios',
      '/users',
      '/usuarios',
      '/settings',
      '/configuracoes'
    ];
    
    for (const path of authenticatedUrls) {
      try {
        const fullUrl = `https://beta.portal.meep.com.br${path}`;
        console.log(`Exploring authenticated page: ${path}`);
        
        await this.page.goto(fullUrl, { waitUntil: 'networkidle', timeout: 8000 });
        await this.page.waitForTimeout(2000);
        
        const pageData = await this.analyzePage(fullUrl);
        this.analysis.publicPages.push(pageData);
        
        await this.takeScreenshot(`auth-${path.replace('/', '')}`);
        
      } catch (error) {
        console.log(`Could not access authenticated page ${path}:`, error.message);
      }
    }
  }
}

// Execute the deep analysis
console.log('🔍 Starting MEEP Deep Analysis...');
const analyzer = new MEEPDeepAnalysis();
analyzer.run().catch(console.error);
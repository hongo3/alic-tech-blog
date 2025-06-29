"""
記事コンテンツのパーツを定義
"""

# セキュリティコンテンツのコード例
SECURITY_JS_CODE_1 = '''```javascript
// BeyondCorpアクセスプロキシの実装例（Node.js）
const express = require('express');
const jwt = require('jsonwebtoken');
const { AuthenticationClient } = require('auth0');

class BeyondCorpAccessProxy {
    constructor(config) {
        this.config = config;
        this.app = express();
        this.trustEngine = new TrustInferenceEngine();
        this.setupMiddleware();
    }
    
    setupMiddleware() {
        // リクエストログ
        this.app.use(this.logRequest.bind(this));
        
        // デバイス検証
        this.app.use(this.verifyDevice.bind(this));
        
        // ユーザー認証
        this.app.use(this.authenticateUser.bind(this));
        
        // 信頼度評価
        this.app.use(this.evaluateTrust.bind(this));
        
        // アクセス制御
        this.app.use(this.enforceAccessControl.bind(this));
    }
    
    async verifyDevice(req, res, next) {
        const deviceId = req.headers['x-device-id'];
        const deviceCert = req.headers['x-device-cert'];
        
        try {
            // デバイス証明書の検証
            const device = await this.validateDeviceCertificate(deviceCert);
            
            // デバイスインベントリとの照合
            const deviceInfo = await this.getDeviceInfo(deviceId);
            
            // コンプライアンスチェック
            const compliance = await this.checkDeviceCompliance(deviceInfo);
            
            if (!compliance.isCompliant) {
                return res.status(403).json({
                    error: 'Device not compliant',
                    issues: compliance.issues
                });
            }
            
            req.device = {
                id: deviceId,
                info: deviceInfo,
                trustScore: compliance.trustScore
            };
            
            next();
        } catch (error) {
            console.error('Device verification failed:', error);
            res.status(403).json({ error: 'Device verification failed' });
        }
    }
    
    async authenticateUser(req, res, next) {
        const token = req.headers.authorization?.split(' ')[1];
        
        if (!token) {
            return res.status(401).json({ error: 'No token provided' });
        }
        
        try {
            // JWTトークンの検証
            const decoded = jwt.verify(token, this.config.jwtSecret);
            
            // ユーザー情報の取得
            const user = await this.getUserInfo(decoded.sub);
            
            // MFA要求の確認
            if (this.requiresMFA(req) && !decoded.amr?.includes('mfa')) {
                return res.status(401).json({ 
                    error: 'MFA required',
                    mfaEndpoint: '/auth/mfa'
                });
            }
            
            req.user = user;
            next();
        } catch (error) {
            console.error('Authentication failed:', error);
            res.status(401).json({ error: 'Authentication failed' });
        }
    }
    
    async evaluateTrust(req, res, next) {
        const trustContext = {
            user: req.user,
            device: req.device,
            request: {
                ip: req.ip,
                userAgent: req.headers['user-agent'],
                timestamp: new Date(),
                resource: req.path,
                method: req.method
            }
        };
        
        // 信頼度スコアの計算
        const trustScore = await this.trustEngine.calculateTrustScore(trustContext);
        
        // 異常検知
        const anomalies = await this.trustEngine.detectAnomalies(trustContext);
        
        req.trustContext = {
            score: trustScore,
            anomalies: anomalies,
            riskLevel: this.calculateRiskLevel(trustScore, anomalies)
        };
        
        // リスクレベルに応じた対応
        if (req.trustContext.riskLevel === 'high') {
            // 追加認証を要求
            return res.status(401).json({
                error: 'Additional authentication required',
                reason: 'High risk detected',
                authMethods: ['biometric', 'hardware_key']
            });
        }
        
        next();
    }
}

// 信頼推論エンジン
class TrustInferenceEngine {
    constructor() {
        this.mlModel = this.loadMLModel();
        this.rules = this.loadTrustRules();
    }
    
    async calculateTrustScore(context) {
        const scores = {
            identity: await this.scoreIdentity(context.user),
            device: await this.scoreDevice(context.device),
            behavior: await this.scoreBehavior(context),
            network: await this.scoreNetwork(context.request)
        };
        
        // 重み付け平均
        const weights = {
            identity: 0.3,
            device: 0.25,
            behavior: 0.25,
            network: 0.2
        };
        
        let totalScore = 0;
        for (const [key, weight] of Object.entries(weights)) {
            totalScore += scores[key] * weight;
        }
        
        return totalScore;
    }
    
    async detectAnomalies(context) {
        const anomalies = [];
        
        // 位置情報の異常検知
        const locationAnomaly = await this.checkLocationAnomaly(context);
        if (locationAnomaly) anomalies.push(locationAnomaly);
        
        // アクセスパターンの異常検知
        const patternAnomaly = await this.checkAccessPattern(context);
        if (patternAnomaly) anomalies.push(patternAnomaly);
        
        // デバイスの異常検知
        const deviceAnomaly = await this.checkDeviceAnomaly(context);
        if (deviceAnomaly) anomalies.push(deviceAnomaly);
        
        return anomalies;
    }
}
```'''

SECURITY_GO_CODE = '''```go
// Go言語でのデバイストラストサービス
package devicetrust

import (
    "crypto/x509"
    "encoding/json"
    "time"
    "github.com/google/uuid"
)

// Device represents a managed device
type Device struct {
    ID                string                 `json:"id"`
    SerialNumber      string                 `json:"serial_number"`
    Manufacturer      string                 `json:"manufacturer"`
    Model            string                 `json:"model"`
    OS               OSInfo                 `json:"os"`
    Owner            string                 `json:"owner"`
    Certificate      *x509.Certificate      `json:"-"`
    TrustLevel       TrustLevel             `json:"trust_level"`
    ComplianceStatus ComplianceStatus       `json:"compliance_status"`
    LastSeen         time.Time              `json:"last_seen"`
    Attributes       map[string]interface{} `json:"attributes"`
}

// TrustLevel represents device trust level
type TrustLevel int

const (
    TrustLevelUntrusted TrustLevel = iota
    TrustLevelBasic
    TrustLevelManaged
    TrustLevelFullyTrusted
)

// DeviceTrustService manages device trust
type DeviceTrustService struct {
    store           DeviceStore
    policyEngine    *PolicyEngine
    attestationSvc  *AttestationService
    inventorySvc    *InventoryService
}

// EvaluateDeviceTrust evaluates the trust level of a device
func (s *DeviceTrustService) EvaluateDeviceTrust(deviceID string) (*TrustEvaluation, error) {
    device, err := s.store.GetDevice(deviceID)
    if err != nil {
        return nil, err
    }
    
    evaluation := &TrustEvaluation{
        DeviceID:   deviceID,
        Timestamp:  time.Now(),
        Factors:    make(map[string]TrustFactor),
    }
    
    // Factor 1: Device Attestation
    attestation, err := s.attestationSvc.VerifyAttestation(device)
    if err == nil && attestation.Valid {
        evaluation.Factors["attestation"] = TrustFactor{
            Name:   "Device Attestation",
            Score:  attestation.Score,
            Weight: 0.3,
        }
    }
    
    // Factor 2: Compliance Status
    compliance := s.evaluateCompliance(device)
    evaluation.Factors["compliance"] = TrustFactor{
        Name:   "Compliance Status",
        Score:  compliance.Score,
        Weight: 0.25,
    }
    
    // Factor 3: Security Posture
    securityPosture := s.evaluateSecurityPosture(device)
    evaluation.Factors["security"] = TrustFactor{
        Name:   "Security Posture",
        Score:  securityPosture.Score,
        Weight: 0.25,
    }
    
    // Factor 4: Device History
    history := s.evaluateDeviceHistory(device)
    evaluation.Factors["history"] = TrustFactor{
        Name:   "Device History",
        Score:  history.Score,
        Weight: 0.2,
    }
    
    // Calculate overall trust score
    evaluation.OverallScore = s.calculateOverallScore(evaluation.Factors)
    evaluation.TrustLevel = s.determineTrustLevel(evaluation.OverallScore)
    
    // Apply policies
    evaluation.PolicyResults = s.policyEngine.Evaluate(device, evaluation)
    
    return evaluation, nil
}

// evaluateCompliance checks device compliance
func (s *DeviceTrustService) evaluateCompliance(device *Device) ComplianceResult {
    result := ComplianceResult{
        Compliant: true,
        Score:     1.0,
        Issues:    []ComplianceIssue{},
    }
    
    // Check OS version
    if !s.isOSVersionCompliant(device.OS) {
        result.Issues = append(result.Issues, ComplianceIssue{
            Type:        "os_version",
            Severity:    "high",
            Description: "Operating system version is outdated",
        })
        result.Score -= 0.3
    }
    
    // Check security patches
    patchLevel := s.inventorySvc.GetPatchLevel(device.ID)
    if patchLevel.DaysBehind > 30 {
        result.Issues = append(result.Issues, ComplianceIssue{
            Type:        "security_patches",
            Severity:    "critical",
            Description: "Security patches are more than 30 days old",
        })
        result.Score -= 0.4
    }
    
    // Check encryption status
    if !device.Attributes["disk_encrypted"].(bool) {
        result.Issues = append(result.Issues, ComplianceIssue{
            Type:        "encryption",
            Severity:    "high",
            Description: "Disk encryption is not enabled",
        })
        result.Score -= 0.3
    }
    
    // Check antivirus status
    avStatus := device.Attributes["antivirus_status"].(map[string]interface{})
    if !avStatus["enabled"].(bool) || !avStatus["up_to_date"].(bool) {
        result.Issues = append(result.Issues, ComplianceIssue{
            Type:        "antivirus",
            Severity:    "medium",
            Description: "Antivirus is not properly configured",
        })
        result.Score -= 0.2
    }
    
    result.Compliant = len(result.Issues) == 0
    result.Score = max(0, result.Score)
    
    return result
}

// AttestationService handles device attestation
type AttestationService struct {
    tpmClient     TPMClient
    certValidator CertificateValidator
}

// VerifyAttestation verifies device attestation
func (a *AttestationService) VerifyAttestation(device *Device) (*AttestationResult, error) {
    result := &AttestationResult{
        DeviceID:  device.ID,
        Timestamp: time.Now(),
    }
    
    // Verify TPM attestation
    if device.Attributes["has_tpm"].(bool) {
        tpmQuote, err := a.tpmClient.GetQuote(device.ID)
        if err != nil {
            return result, err
        }
        
        // Verify TPM quote
        valid, err := a.tpmClient.VerifyQuote(tpmQuote, device.Certificate)
        if err != nil {
            return result, err
        }
        
        if valid {
            result.Valid = true
            result.Score = 1.0
            result.Method = "TPM"
        }
    } else {
        // Fall back to software attestation
        result.Valid = true
        result.Score = 0.6
        result.Method = "Software"
    }
    
    return result, nil
}
```'''

NEXTJS_CODE_1 = '''```typescript
// app/layout.tsx - ルートレイアウト
import { Inter } from 'next/font/google'
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: {
    default: 'Next.js 15 App',
    template: '%s | Next.js 15 App'
  },
  description: 'App Router × Server Components × Streaming',
  openGraph: {
    title: 'Next.js 15 App',
    description: 'Modern web application with Next.js 15',
    url: 'https://example.com',
    siteName: 'Next.js 15 App',
    images: [
      {
        url: 'https://example.com/og.png',
        width: 1200,
        height: 630,
      }
    ],
    locale: 'ja_JP',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Next.js 15 App',
    description: 'Modern web application with Next.js 15',
    creator: '@yourusername',
    images: ['https://example.com/og.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja" className={inter.className}>
      <body>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
          {children}
        </div>
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
```'''

NEXTJS_CODE_2 = '''```typescript
// app/products/[category]/[id]/page.tsx
import { notFound } from 'next/navigation'
import { Suspense } from 'react'
import { ProductDetail } from '@/components/ProductDetail'
import { ProductSkeleton } from '@/components/ProductSkeleton'
import { getProduct, getProductCategories } from '@/lib/api'

interface PageProps {
  params: {
    category: string
    id: string
  }
  searchParams: {
    [key: string]: string | string[] | undefined
  }
}

// 動的メタデータ生成
export async function generateMetadata({ params }: PageProps) {
  const product = await getProduct(params.category, params.id)
  
  if (!product) {
    return {
      title: 'Product Not Found',
    }
  }
  
  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [product.image],
    },
  }
}

// 静的パラメータの生成（SSG用）
export async function generateStaticParams() {
  const categories = await getProductCategories()
  const paths = []
  
  for (const category of categories) {
    const products = await getProductsByCategory(category.slug)
    for (const product of products) {
      paths.push({
        category: category.slug,
        id: product.id,
      })
    }
  }
  
  return paths
}

export default async function ProductPage({ params, searchParams }: PageProps) {
  const product = await getProduct(params.category, params.id)
  
  if (!product) {
    notFound()
  }
  
  // レビューやレコメンドは別途ストリーミング
  return (
    <div className="container mx-auto px-4 py-8">
      <ProductDetail product={product} />
      
      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews productId={product.id} />
      </Suspense>
      
      <Suspense fallback={<RecommendationsSkeleton />}>
        <ProductRecommendations 
          category={params.category} 
          currentProductId={product.id} 
        />
      </Suspense>
    </div>
  )
}

// レビューコンポーネント（Server Component）
async function ProductReviews({ productId }: { productId: string }) {
  const reviews = await getProductReviews(productId)
  
  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold mb-6">カスタマーレビュー</h2>
      <div className="space-y-4">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>
    </div>
  )
}

// レコメンデーションコンポーネント（Server Component）
async function ProductRecommendations({ 
  category, 
  currentProductId 
}: { 
  category: string
  currentProductId: string 
}) {
  const recommendations = await getRecommendations(category, currentProductId)
  
  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold mb-6">おすすめ商品</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {recommendations.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  )
}
```'''
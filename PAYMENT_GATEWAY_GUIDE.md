# Payment Gateway Integration Guide

## Overview
The UVTech Neighbourhood Service Marketplace now features a complete payment gateway integration with commission tracking. The system enables users to pay for services via QR codes and tracks provider balances and commissions.

## Key Features

### 1. **Payment Processing (Razorpay)**
- **QR Code Generation**: Each payment order generates a unique QR code for UPI payment
- **Multiple Payment Methods**: Support for card, netbanking, UPI, and other Razorpay methods
- **Payment Verification**: Automatic signature verification for secure transactions
- **Order Management**: 15-minute payment order expiration

### 2. **Commission System (20%)**
- **Automatic Calculation**: Platform automatically calculates 20% commission on each service
- **Provider Earnings**: Providers receive 80% of service price
- **Commission Tracking**: Detailed transaction history for all commission calculations
- **Balance Tracking**: Real-time provider balance updates

### 3. **Provider Balance Management**
- **Earnings Tracking**: Total earnings from completed services
- **Commission Owed**: Amount owed to the platform
- **Current Balance**: Net balance (Positive = Healthy, Negative = In Debt)
- **Account Suspension**: Automatic suspension for negative balance exceeding 30 days

## System Architecture

### Models

#### 1. **Payment Model**
Stores complete payment transaction details:
- Booking reference
- Customer and Provider information
- Amount breakdown (commission + provider share)
- Razorpay transaction IDs and signature
- Payment status (pending/completed/failed/cancelled)

#### 2. **ProviderBalance Model**
Tracks provider's financial status:
- Total earnings from all completed services
- Total commission owed to platform
- Current balance (calculated automatically)
- Suspension status (for negative balance)

#### 3. **PaymentOrder Model**
Manages payment order lifecycle:
- Razorpay order ID
- QR code image
- Payment status
- Expiration timestamp

#### 4. **CommissionTransaction Model**
Audit trail for all commission activities:
- Transaction type (service_payment, commission_payment, refund)
- Amount and description
- Status tracking

### Payment Flow

```
1. Customer Books Service
   ↓
2. Customer Pays (via QR Code/Payment Page)
   ↓
3. Payment Verified with Razorpay
   ↓
4. Booking marked as Paid
   ↓
5. Provider Balance Updated
   ├─ Earnings: +80% of payment
   └─ Commission Owed: +20% of payment
   ↓
6. Service Completion & Review
```

## Configuration

### Environment Setup

1. **Razorpay Keys** (in `settings.py`):
```python
RAZORPAY_KEY_ID = 'your_test_key_here'
RAZORPAY_KEY_SECRET = 'your_test_secret_here'
```

2. **Commission Rate**:
```python
COMPANY_COMMISSION_PERCENTAGE = 20  # 20% commission
```

3. **Payment Settings**:
```python
PAYMENT_EXPIRY_MINUTES = 15  # Order expires in 15 minutes
QR_CODE_SIZE = 10  # QR code module size
```

## API Endpoints

### Payment Endpoints

#### 1. **Initiate Payment**
- **URL**: `/payment/<booking_id>/initiate/`
- **Method**: GET
- **Auth**: Required (Customer only)
- **Response**: Payment page with QR code
- **Functionality**: 
  - Creates Razorpay order
  - Generates QR code
  - Displays payment details

#### 2. **Verify Payment**
- **URL**: `/payment/<booking_id>/verify/`
- **Method**: POST
- **Auth**: Required (Customer)
- **Payload**:
  ```json
  {
    "razorpay_payment_id": "pay_xxx",
    "razorpay_order_id": "order_xxx",
    "razorpay_signature": "sig_xxx"
  }
  ```
- **Response**: JSON with success/error status
- **Functionality**:
  - Verifies Razorpay signature
  - Creates Payment record
  - Updates booking status
  - Updates provider balance

#### 3. **Payment Success**
- **URL**: `/payment/<booking_id>/success/`
- **Method**: GET
- **Auth**: Required (Customer)
- **Response**: Success confirmation page

#### 4. **Provider Earnings Dashboard**
- **URL**: `/earnings/`
- **Method**: GET
- **Auth**: Required (Provider only)
- **Response**: Earnings dashboard HTML
- **Includes**:
  - Total earnings
  - Total commission owed
  - Current balance status
  - Payment history
  - Commission transaction log

## Customer Journey

### 1. **Browse and Book Service**
- Customer finds service
- Clicks "Book Service"
- Provides booking details

### 2. **Make Payment**
- Customer navigates to manage bookings
- Clicks "💳 Pay Now" button
- Views payment page with:
  - Service details
  - QR code
  - Amount breakdown
  - Commission explanation

### 3. **Complete Payment**
- Customer scans QR with UPI app
- Verifies amount and completes payment
- Automatically updated on payment page

### 4. **Post-Payment**
- Can message provider
- Can track booking status
- Can leave review after completion

## Provider Journey

### 1. **View Earnings Dashboard**
- Navigates to "💰 Earnings & Commission"
- Views:
  - Total earnings
  - Commission owed
  - Current balance status
  - Payment history

### 2. **Understand Commission Breakdown**
For example, if service price is ₹100:
- Service amount: ₹100
- Company commission (20%): -₹20
- Provider receives: ₹80

### 3. **Monitor Balance**
- **Positive Balance**: Good standing ✓
- **Negative Balance**: Owes commission ⚠️
  - Can view outstanding amount
  - May face account suspension
  - Cannot list new services if suspended

### 4. **Account Status**
- **Active**: Can provide services and receive bookings
- **Suspended**: Cannot list services if balance is negative for 30+ days

## Database Queries

### Get Provider Balance
```python
from marketplace.models import ProviderBalance

provider_balance = ProviderBalance.objects.get(provider=user)
print(f"Earnings: {provider_balance.total_earnings}")
print(f"Commission Owed: {provider_balance.total_commission_owed}")
print(f"Balance: {provider_balance.current_balance}")
```

### Get Payment History
```python
from marketplace.models import Payment

payments = Payment.objects.filter(
    service_provider=user,
    status='completed'
).order_by('-created_at')
```

### Get Commission Transactions
```python
from marketplace.models import CommissionTransaction

transactions = CommissionTransaction.objects.filter(
    provider=user
).order_by('-created_at')
```

## Payment Status Indicators

### Booking Status in Manage Bookings
- ⏳ **Pending Payment**: Customer hasn't paid yet
- ✓ **Payment Received**: Payment confirmed and processed
- Shows on each booking card for quick reference

### Provider Balance Status
- 🟢 **Positive Balance**: Account in good standing
- 🔴 **Negative Balance**: Commission payment required
- Alert shown if balance negative for 30+ days

## Testing

### Test Razorpay Credentials
For development, use Razorpay's test keys:
- Test Key ID: `rzp_test_1A2B3C4D5E6F7G8H`
- Test Key Secret: `wXyZaBcDeFgHiJkLmNoP`

### Test UPI Payments
Razorpay provides test UPI IDs for testing purposes. Check official documentation.

## Security Considerations

1. **Signature Verification**: All payments verified using Razorpay's signature
2. **Sensitive Keys**: Razorpay keys stored in settings (use environment variables in production)
3. **Authorization Checks**: Only customers can initiate/verify their own payments
4. **Data Encryption**: Razorpay handles data encryption and PCI compliance
5. **HTTPS Only**: Ensure production uses HTTPS for payment pages

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: razorpay"**
   - Solution: `pip install razorpay`

2. **"Invalid Razorpay credentials"**
   - Check settings.py for correct key and secret
   - Ensure using correct test/production keys

3. **QR Code Not Generating**
   - Ensure `qrcode` package installed: `pip install qrcode[pil]`
   - Check media directory permissions

4. **Payment Verification Fails**
   - Verify all three Razorpay parameters match
   - Check if order exists in Razorpay account
   - Check timestamp alignment

5. **Provider Balance Not Updating**
   - Check Payment status is 'completed'
   - Verify booking.is_paid is set to True
   - Check ProviderBalance record exists

## Integration Checklist

- [ ] Install razorpay: `pip install razorpay`
- [ ] Install qrcode: `pip install qrcode[pil]`
- [ ] Add Razorpay credentials to settings.py
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test payment flow end-to-end
- [ ] Verify provider earnings dashboard
- [ ] Test QR code generation and scanning
- [ ] Verify commission calculations
- [ ] Test balance status indicators
- [ ] Setup production Razorpay keys

## Future Enhancements

1. **Commission Payment Integration**
   - Generate commission payment links for batchsettlement
   - Track commission payments from providers

2. **Advanced Analytics**
   - Earnings reports and charts
   - Commission analytics
   - Revenue forecasting

3. **Automated Payouts**
   - Automatic settlement of provider earnings
   - Bank transfer integration

4. **Dispute Resolution**
   - Refund management
   - Dispute tracking system

## Support & Documentation

For Razorpay integration details, visit: https://razorpay.com/docs/

For questions or issues, contact: support@uvtech.local

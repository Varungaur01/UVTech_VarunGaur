# Quick Start Guide - Payment Gateway Testing

## 🚀 Getting Started

### Step 1: Install Dependencies
```bash
cd c:\Users\VARUN\Desktop\kp\UVTech_VarunGaur
pip install razorpay qrcode[pil]
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Start the Development Server
```bash
python manage.py runserver
```

The server will be running at `http://127.0.0.1:8000/`

---

## 💳 Testing the Payment Flow

### Option A: Full End-to-End Test

#### 1. Create Test Accounts
```
Customer Account:
- Username: testcustomer
- Password: test123456

Provider Account:
- Username: testprovider
- Password: test123456
```

#### 2. Set Up a Service
- Login as provider
- Go to Dashboard → Add Service
- Create a test service (e.g., "Test Service - ₹100")
- Note the service price

#### 3. Book the Service
- Logout and login as customer
- Browse services
- Book the test service
- Note the booking ID

#### 4. Initiate Payment
- Go to Manage Bookings
- Click "💳 Pay Now"
- You should see:
  - QR code
  - Service details
  - Amount breakdown
  - Order ID

#### 5. Test Payment Verification
- The payment will be verified (in test mode)
- See the success page with:
  - Order confirmation
  - Payment details
  - "View My Bookings" link

### Option B: Quick Test (Without QR Scanning)
- Navigate to `/payment/<booking_id>/initiate/`
- View the payment page
- Check QR code generation
- Verify order ID creation

---

## 👁️ Viewing Results

### For Customers:
1. Go to "Manage Bookings"
2. Look for status badges:
   - **⏳ Pending Payment**: Not yet paid
   - **✓ Payment Received**: Payment confirmed

### For Providers:
1. Go to Dashboard
2. Click "💰 Earnings & Commission"
3. View:
   - Total Earnings (80% of service price)
   - Commission Owed (20% of service price)
   - Current Balance
   - Payment History Table

---

## 💻 Database Verification

### Check Payments in Django Shell
```bash
python manage.py shell
```

```python
from marketplace.models import Payment, ProviderBalance, Booking

# View all payments
payments = Payment.objects.all()
for payment in payments:
    print(f"Amount: {payment.amount}, Commission: {payment.company_commission}, Provider: {payment.provider_amount}")

# Check provider balance
balance = ProviderBalance.objects.first()
print(f"Total Earnings: {balance.total_earnings}")
print(f"Commission Owed: {balance.total_commission_owed}")
print(f"Current Balance: {balance.current_balance}")
```

---

## 🐛 Troubleshooting Common Issues

### Issue 1: QR Code Not Displaying
**Error**: QR code image not showing on payment page

**Solution**:
1. Check media directory exists: `mkdir -p media/qr_codes/`
2. Verify permissions: `chmod 755 media/`
3. Check disk space for media files
4. Restart Django server

### Issue 2: Payment Verification Fails
**Error**: "Payment signature verification failed"

**Solution**:
1. Verify Razorpay keys in settings.py match your account
2. Check that all three parameters match (payment_id, order_id, signature)
3. Ensure correct Razorpay environment (test vs production)
4. Check system clock synchronization

### Issue 3: Provider Balance Not Updated
**Error**: Earnings don't appear in provider dashboard

**Solution**:
1. Confirm booking.is_paid = True in database
2. Verify Payment record exists with status='completed'
3. Check ProviderBalance record exists for the provider
4. Run this in Django shell:
   ```python
   balance = ProviderBalance.objects.get(provider_id=<user_id>)
   balance.update_balance()  # Force recalculation
   ```

### Issue 4: Module Not Found Errors
**Error**: "No module named 'razorpay'" or "No module named 'qrcode'"

**Solution**:
```bash
pip install razorpay --upgrade
pip install qrcode[pil] --upgrade
```

---

## 📊 Example Test Data

### Test Service Prices:
- ₹100 → Provider Gets ₹80, UVTech Gets ₹20
- ₹500 → Provider Gets ₹400, UVTech Gets ₹100
- ₹1000 → Provider Gets ₹800, UVTech Gets ₹200

### Test Scenarios:

#### Scenario 1: Single Payment
1. Customer pays for 1 service at ₹100
2. Provider earnings: ₹80
3. Commission owed: ₹20
4. Balance: ₹60 (if first payment)

#### Scenario 2: Multiple Payments
1. First service: ₹100 → P:₹80, C:₹20
2. Second service: ₹100 → P:₹80, C:₹20
3. Total B: ₹120 (P:₹160 - C:₹40)

#### Scenario 3: Negative Balance
1. Commission owed: ₹500
2. Current earnings: ₹300
3. Balance: -₹200 (In Debt)
4. Account Status: May be suspended

---

## 🔍 Verification Checklist

After implementing payments, verify:

- [ ] QR code generates and displays correctly
- [ ] Payment page shows correct service details
- [ ] Amount breakdown correctly shows 20% commission
- [ ] Payment verification doesn't crash
- [ ] Booking is marked as paid (is_paid=True)
- [ ] Payment record created in database
- [ ] ProviderBalance record created
- [ ] Provider earnings updated correctly
- [ ] Commission transaction logged
- [ ] Success page displays after payment
- [ ] Provider earnings dashboard shows data
- [ ] Payment history table populates
- [ ] Commission calculation is 20% of service price

---

## 📱 Test with Real UPI

To test with actual UPI payment:

1. **Get Production Razorpay Keys**
   - Go to https://dashboard.razorpay.com/
   - Verify business account
   - Get production keys

2. **Update settings.py**
   ```python
   RAZORPAY_KEY_ID = 'rzp_live_your_key_here'
   RAZORPAY_KEY_SECRET = 'your_secret_here'
   ```

3. **Set DEBUG = False** in production

4. **Use HTTPS** only

5. **Test Payment**
   - Complete actual payment from your UPI app
   - Verify in Razorpay dashboard

---

## 🔑 Razorpay Dashboard

### Monitor Payments:
1. Go to https://dashboard.razorpay.com/
2. View payment status
3. Check settlement details
4. Download payment reports

### Check Webhooks (if setup):
- Verify webhook URL configured
- Check webhook logs
- Monitor delivery status

---

## 📞 Quick Reference

### API Endpoints:
- Payment Initiation: `/payment/<booking_id>/initiate/`
- Payment Verification: `/payment/<booking_id>/verify/`
- Payment Success: `/payment/<booking_id>/success/`
- Provider Earnings: `/earnings/`

### Database Tables:
- `marketplace_payment` - Payment transactions
- `marketplace_providerbalance` - Provider balances
- `marketplace_paymentorder` - QR code orders
- `marketplace_commissiontransaction` - Commission audit log

### Test Commands:
```bash
# Check payment status
python manage.py shell
>>> from marketplace.models import Payment
>>> Payment.objects.filter(status='completed').count()

# Recalculate balances
>>> from marketplace.models import ProviderBalance
>>> for balance in ProviderBalance.objects.all():
...     balance.update_balance()

# View commission transactions
>>> from marketplace.models import CommissionTransaction
>>> CommissionTransaction.objects.all().values('provider__username', 'amount')
```

---

## 🎯 Next Steps

1. ✅ Test the payment flow end-to-end
2. ✅ Verify provider earnings dashboard
3. ✅ Check commission calculations
4. ✅ Review database records
5. ✅ Test edge cases (negative balance, etc.)
6. ✅ Setup production Razorpay keys
7. ✅ Configure HTTPS for production
8. ✅ Deploy to production server

---

**Happy Testing! 🎉**

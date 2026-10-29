import fs from 'fs';
import path from 'path';

const DATA_DIR = path.resolve(import.meta.dirname, '../data');
const NUMBERS_FILE = path.join(DATA_DIR, 'numbers.json');
const ORDERS_FILE = path.join(DATA_DIR, 'orders.json');

// Helper to read database
function getNumbersDb() {
  try {
    if (fs.existsSync(NUMBERS_FILE)) {
      return JSON.parse(fs.readFileSync(NUMBERS_FILE, 'utf-8'));
    }
  } catch (e) {
    console.error('Error reading numbers database:', e);
  }
  return [];
}

function getOrdersDb() {
  try {
    if (fs.existsSync(ORDERS_FILE)) {
      const content = fs.readFileSync(ORDERS_FILE, 'utf-8').trim();
      return content ? JSON.parse(content) : [];
    }
  } catch (e) {
    console.error('Error reading orders database:', e);
  }
  return [];
}

function saveOrdersDb(orders) {
  try {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    fs.writeFileSync(ORDERS_FILE, JSON.stringify(orders, null, 2), 'utf-8');
    return true;
  } catch (e) {
    console.error('Error saving orders database:', e);
    return false;
  }
}

// Indian mobile regex: 10 digits starting with 6, 7, 8, or 9
const INDIAN_PHONE_REGEX = /^[6-9]\d{9}$/;
// Indian PIN code regex: exactly 6 digits
const PINCODE_REGEX = /^\d{6}$/;

export function validateOrderInput(data) {
  const errors = {};

  // 1. Full Name
  if (!data.fullName || typeof data.fullName !== 'string' || data.fullName.trim().length < 2) {
    errors.fullName = 'Full Name is required (minimum 2 characters)';
  }

  // 2. Mobile Number
  const cleanMobile = data.mobileNumber ? String(data.mobileNumber).replace(/\D/g, '') : '';
  if (!cleanMobile || !INDIAN_PHONE_REGEX.test(cleanMobile)) {
    errors.mobileNumber = 'Valid 10-digit Indian mobile number required (starting with 6-9)';
  }

  // 3. WhatsApp Number
  const cleanWhatsapp = data.whatsappNumber ? String(data.whatsappNumber).replace(/\D/g, '') : '';
  if (!cleanWhatsapp || !INDIAN_PHONE_REGEX.test(cleanWhatsapp)) {
    errors.whatsappNumber = 'Valid 10-digit WhatsApp number required';
  }

  // 4. Full Address
  if (!data.address || typeof data.address !== 'string' || data.address.trim().length < 5) {
    errors.address = 'Full address including house/flat, street & locality is required';
  }

  // 5. PIN Code
  const cleanPincode = data.pincode ? String(data.pincode).trim() : '';
  if (!cleanPincode || !PINCODE_REGEX.test(cleanPincode)) {
    errors.pincode = 'PIN Code must be exactly 6 digits';
  }

  // 6. State
  if (!data.state || typeof data.state !== 'string' || data.state.trim().length < 2) {
    errors.state = 'State is required';
  }

  // 7. City
  if (!data.city || typeof data.city !== 'string' || data.city.trim().length < 2) {
    errors.city = 'City is required';
  }

  // VIP Number
  const cleanVipNumber = data.vipNumber ? String(data.vipNumber).replace(/\D/g, '') : '';
  if (!cleanVipNumber || cleanVipNumber.length !== 10) {
    errors.vipNumber = 'A valid 10-digit VIP mobile number must be selected';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    sanitized: {
      fullName: data.fullName ? data.fullName.trim() : '',
      mobileNumber: cleanMobile,
      whatsappNumber: cleanWhatsapp,
      address: data.address ? data.address.trim() : '',
      pincode: cleanPincode,
      state: data.state ? data.state.trim() : '',
      city: data.city ? data.city.trim() : '',
      vipNumber: cleanVipNumber,
      paymentMethod: data.paymentMethod ? String(data.paymentMethod).trim() : 'UPI'
    }
  };
}

export function ordersApiMiddleware(req, res, next) {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname;

  if (pathname !== '/api/orders' && pathname !== '/api/orders/') {
    return next();
  }

  // GET /api/orders or /api/orders?orderId=...
  if (req.method === 'GET') {
    const orderId = url.searchParams.get('orderId');
    const orders = getOrdersDb();
    res.setHeader('Content-Type', 'application/json');

    if (orderId) {
      const found = orders.find(o => o.orderId === orderId);
      if (found) {
        res.statusCode = 200;
        return res.end(JSON.stringify({ success: true, order: found }));
      } else {
        res.statusCode = 404;
        return res.end(JSON.stringify({ success: false, message: 'Order not found' }));
      }
    }

    res.statusCode = 200;
    return res.end(JSON.stringify({ success: true, count: orders.length, orders }));
  }

  // POST /api/orders
  if (req.method === 'POST') {
    let rawBody = '';
    req.on('data', chunk => {
      rawBody += chunk;
      // Protect against too large payload
      if (rawBody.length > 1e6) {
        req.destroy();
      }
    });

    req.on('end', () => {
      let payload;
      try {
        payload = JSON.parse(rawBody);
      } catch (err) {
        res.statusCode = 400;
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify({ success: false, message: 'Invalid JSON payload' }));
      }

      // Server-side validation
      const validation = validateOrderInput(payload);
      if (!validation.isValid) {
        res.statusCode = 400;
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify({
          success: false,
          message: 'Validation failed',
          errors: validation.errors
        }));
      }

      const { sanitized } = validation;

      // Verify number against actual database
      const numbersDb = getNumbersDb();
      const dbRecord = numbersDb.find(n => n.number === sanitized.vipNumber);
      
      // Preserve database actual price and category
      const finalAmount = dbRecord ? dbRecord.price : (Number(payload.price) || 12250);
      const originalPrice = dbRecord ? dbRecord.originalPrice : (Number(payload.originalPrice) || Math.round(finalAmount * 1.5));
      const category = dbRecord ? dbRecord.category : (payload.category || 'VIP Mobile Number');
      const discount = Math.max(0, originalPrice - finalAmount);

      const existingOrders = getOrdersDb();

      // Check for duplicate submission within last 5 minutes (same VIP number + same customer mobile)
      const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
      const duplicateOrder = existingOrders.find(o => 
        o.vipNumber === sanitized.vipNumber &&
        o.customer.mobileNumber === sanitized.mobileNumber &&
        o.paymentStatus === 'pending' &&
        new Date(o.createdAt).getTime() > fiveMinutesAgo
      );

      if (duplicateOrder) {
        // Update customer details if any field changed
        duplicateOrder.customer = {
          fullName: sanitized.fullName,
          mobileNumber: sanitized.mobileNumber,
          whatsappNumber: sanitized.whatsappNumber,
          address: sanitized.address,
          pincode: sanitized.pincode,
          state: sanitized.state,
          city: sanitized.city
        };
        duplicateOrder.paymentMethod = sanitized.paymentMethod;
        duplicateOrder.updatedAt = new Date().toISOString();
        saveOrdersDb(existingOrders);

        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify({
          success: true,
          isDuplicate: true,
          message: 'Existing pending order updated',
          orderId: duplicateOrder.orderId,
          order: duplicateOrder
        }));
      }

      // Generate unique Order ID: ORD-VIP-<TIMESTAMP>-<RANDOM>
      const randHex = Math.random().toString(36).substring(2, 6).toUpperCase();
      const orderId = `ORD-VIP-${Date.now().toString(36).toUpperCase()}-${randHex}`;

      const newOrder = {
        orderId,
        vipNumber: sanitized.vipNumber,
        displayNumber: `${sanitized.vipNumber.slice(0, 5)} ${sanitized.vipNumber.slice(5)}`,
        category,
        amount: finalAmount,
        originalPrice,
        discount,
        customer: {
          fullName: sanitized.fullName,
          mobileNumber: sanitized.mobileNumber,
          whatsappNumber: sanitized.whatsappNumber,
          address: sanitized.address,
          pincode: sanitized.pincode,
          state: sanitized.state,
          city: sanitized.city
        },
        paymentMethod: sanitized.paymentMethod,
        paymentStatus: 'pending', // Do NOT mark as paid until gateway verification
        paymentGatewayRef: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      existingOrders.unshift(newOrder);
      saveOrdersDb(existingOrders);

      res.statusCode = 201;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({
        success: true,
        message: 'Order created and details saved successfully',
        orderId: newOrder.orderId,
        order: newOrder
      }));
    });
    return;
  }

  res.statusCode = 405;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ success: false, message: 'Method Not Allowed' }));
}


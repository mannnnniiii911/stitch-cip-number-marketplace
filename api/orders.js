import { getSupabaseClient } from '../server/supabase.js';
import { validateOrderInput } from '../server/orders.js';

export default async function handler(req, res) {
  // Set CORS and JSON headers
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const supabase = getSupabaseClient();
  if (!supabase) {
    return res.status(500).json({
      success: false,
      message: 'Database configuration missing: SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY is not configured.'
    });
  }

  // GET: Fetch order details
  if (req.method === 'GET') {
    const { orderId } = req.query;

    try {
      if (orderId) {
        const { data, error } = await supabase
          .from('orders')
          .select('*')
          .eq('order_id', orderId)
          .single();

        if (error || !data) {
          return res.status(404).json({ success: false, message: 'Order not found' });
        }

        return res.status(200).json({ success: true, order: formatOrderRecord(data) });
      }

      // Default list recent 50 orders
      const { data, error } = await supabase
        .from('orders')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50);

      if (error) {
        return res.status(500).json({ success: false, message: error.message });
      }

      return res.status(200).json({
        success: true,
        count: data.length,
        orders: data.map(formatOrderRecord)
      });
    } catch (err) {
      return res.status(500).json({ success: false, message: err.message });
    }
  }

  // POST: Create or update pending order
  if (req.method === 'POST') {
    let payload = req.body;
    if (typeof payload === 'string') {
      try {
        payload = JSON.parse(payload);
      } catch (e) {
        return res.status(400).json({ success: false, message: 'Invalid JSON payload' });
      }
    }

    const validation = validateOrderInput(payload);
    if (!validation.isValid) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: validation.errors
      });
    }

    const { sanitized } = validation;
    const finalAmount = Number(payload.price) || 12250;
    const originalPrice = Number(payload.originalPrice) || Math.round(finalAmount * 1.5);
    const discount = Math.max(0, originalPrice - finalAmount);
    const category = payload.category || 'VIP Mobile Number';
    const displayNumber = `${sanitized.vipNumber.slice(0, 5)} ${sanitized.vipNumber.slice(5)}`;

    try {
      // Check for duplicate pending submission within last 5 minutes
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
      const { data: duplicateOrders } = await supabase
        .from('orders')
        .select('*')
        .eq('vip_number', sanitized.vipNumber)
        .eq('customer_mobile', sanitized.mobileNumber)
        .eq('payment_status', 'pending')
        .gte('created_at', fiveMinutesAgo)
        .limit(1);

      if (duplicateOrders && duplicateOrders.length > 0) {
        const existing = duplicateOrders[0];
        const { data: updated, error: updateErr } = await supabase
          .from('orders')
          .update({
            customer_name: sanitized.fullName,
            customer_whatsapp: sanitized.whatsappNumber,
            customer_address: sanitized.address,
            customer_city: sanitized.city,
            customer_state: sanitized.state,
            customer_pincode: sanitized.pincode,
            payment_method: sanitized.paymentMethod,
            updated_at: new Date().toISOString()
          })
          .eq('id', existing.id)
          .select()
          .single();

        if (updateErr) {
          return res.status(500).json({ success: false, message: updateErr.message });
        }

        return res.status(200).json({
          success: true,
          isDuplicate: true,
          message: 'Existing pending order updated',
          orderId: updated.order_id,
          order: formatOrderRecord(updated)
        });
      }

      // Generate unique Order ID: ORD-VIP-<TIMESTAMP>-<RANDOM>
      const randHex = Math.random().toString(36).substring(2, 6).toUpperCase();
      const orderId = `ORD-VIP-${Date.now().toString(36).toUpperCase()}-${randHex}`;

      const newRecord = {
        order_id: orderId,
        vip_number: sanitized.vipNumber,
        display_number: displayNumber,
        category,
        amount: finalAmount,
        original_price: originalPrice,
        discount,
        payment_method: sanitized.paymentMethod,
        payment_status: 'pending',
        customer_name: sanitized.fullName,
        customer_mobile: sanitized.mobileNumber,
        customer_whatsapp: sanitized.whatsappNumber,
        customer_address: sanitized.address,
        customer_city: sanitized.city,
        customer_state: sanitized.state,
        customer_pincode: sanitized.pincode,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data: inserted, error: insertErr } = await supabase
        .from('orders')
        .insert(newRecord)
        .select()
        .single();

      if (insertErr) {
        return res.status(500).json({ success: false, message: insertErr.message });
      }

      return res.status(201).json({
        success: true,
        message: 'Order created and details saved successfully',
        orderId: inserted.order_id,
        order: formatOrderRecord(inserted)
      });
    } catch (err) {
      return res.status(500).json({ success: false, message: err.message });
    }
  }

  return res.status(405).json({ success: false, message: 'Method Not Allowed' });
}

function formatOrderRecord(record) {
  return {
    orderId: record.order_id,
    vipNumber: record.vip_number,
    displayNumber: record.display_number,
    category: record.category,
    amount: Number(record.amount),
    originalPrice: Number(record.original_price),
    discount: Number(record.discount),
    customer: {
      fullName: record.customer_name,
      mobileNumber: record.customer_mobile,
      whatsappNumber: record.customer_whatsapp,
      address: record.customer_address,
      pincode: record.customer_pincode,
      state: record.customer_state,
      city: record.customer_city
    },
    paymentMethod: record.payment_method,
    paymentStatus: record.payment_status,
    paymentGatewayRef: record.payment_gateway_ref,
    createdAt: record.created_at,
    updatedAt: record.updated_at
  };
}


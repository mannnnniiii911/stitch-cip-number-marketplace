-- VIP NUMBER CLUB: Orders Database Schema for Supabase PostgreSQL
-- Run this query in the Supabase SQL Editor:

CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id TEXT UNIQUE NOT NULL,
    vip_number TEXT NOT NULL,
    display_number TEXT,
    category TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    original_price NUMERIC(12, 2),
    discount NUMERIC(12, 2),
    payment_method TEXT NOT NULL,
    payment_status TEXT DEFAULT 'pending',
    customer_name TEXT NOT NULL,
    customer_mobile TEXT NOT NULL,
    customer_whatsapp TEXT NOT NULL,
    customer_address TEXT NOT NULL,
    customer_city TEXT NOT NULL,
    customer_state TEXT NOT NULL,
    customer_pincode TEXT NOT NULL,
    payment_gateway_ref TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for speedy lookups
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON public.orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_mobile ON public.orders(customer_mobile);
CREATE INDEX IF NOT EXISTS idx_orders_vip_number ON public.orders(vip_number);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- Allow insert and read via service_role / backend API
CREATE POLICY "Allow server-side service role full access"
    ON public.orders
    FOR ALL
    USING (true)
    WITH CHECK (true);


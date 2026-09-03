--
-- PostgreSQL database dump
--

\restrict KysQ3FSFu1H8WNRvkMR1WPm0RWzXuaxHs0c6Qo6IaEIaX0MxJL1oNCefYR6TOsS

-- Dumped from database version 16.15
-- Dumped by pg_dump version 17.11 (Debian 17.11-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: attendance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    check_in text,
    check_out text,
    date text NOT NULL
);


--
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- Name: backup_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backup_history (
    id integer NOT NULL,
    backup_date text NOT NULL,
    file_name text NOT NULL,
    file_size integer,
    created_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: backup_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backup_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backup_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backup_history_id_seq OWNED BY public.backup_history.id;


--
-- Name: cash_incomes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cash_incomes (
    id integer NOT NULL,
    amount numeric NOT NULL,
    note text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer
);


--
-- Name: cash_incomes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cash_incomes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cash_incomes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cash_incomes_id_seq OWNED BY public.cash_incomes.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name text NOT NULL,
    parent_id integer,
    icon text,
    color text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: debt_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.debt_payments (
    id integer NOT NULL,
    purchase_id integer NOT NULL,
    paid_amount numeric DEFAULT 0 NOT NULL,
    cash_amount numeric DEFAULT 0 NOT NULL,
    card_amount numeric DEFAULT 0 NOT NULL,
    payment_type text DEFAULT 'Naxt'::text,
    paid_date text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: debt_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.debt_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: debt_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.debt_payments_id_seq OWNED BY public.debt_payments.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    full_name text NOT NULL,
    phone text,
    "position" text NOT NULL,
    salary numeric DEFAULT 0,
    hire_date text,
    is_active integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: expenses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    name text NOT NULL,
    amount numeric NOT NULL,
    category text NOT NULL,
    description text,
    payment_type text DEFAULT 'Naxt'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer
);


--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


--
-- Name: firm_debt_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.firm_debt_payments (
    id integer NOT NULL,
    debt_id integer NOT NULL,
    paid_amount numeric DEFAULT 0 NOT NULL,
    cash_amount numeric DEFAULT 0 NOT NULL,
    card_amount numeric DEFAULT 0 NOT NULL,
    payment_type text DEFAULT 'Naxt'::text,
    paid_date text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: firm_debt_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.firm_debt_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: firm_debt_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.firm_debt_payments_id_seq OWNED BY public.firm_debt_payments.id;


--
-- Name: firm_debts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.firm_debts (
    id integer NOT NULL,
    firm_id integer NOT NULL,
    firm_name text,
    amount numeric NOT NULL,
    description text,
    debt_type text DEFAULT 'qarz'::text,
    is_paid integer DEFAULT 0,
    paid_date text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT firm_debts_debt_type_check CHECK ((debt_type = ANY (ARRAY['qarz'::text, 'to_lov'::text])))
);


--
-- Name: firm_debts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.firm_debts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: firm_debts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.firm_debts_id_seq OWNED BY public.firm_debts.id;


--
-- Name: firms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.firms (
    id integer NOT NULL,
    name text NOT NULL,
    phone text,
    address text,
    total_debt numeric DEFAULT 0,
    note text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: firms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.firms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: firms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.firms_id_seq OWNED BY public.firms.id;


--
-- Name: inventory_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_logs (
    id integer NOT NULL,
    product_id integer NOT NULL,
    action text NOT NULL,
    quantity numeric NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer
);


--
-- Name: inventory_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inventory_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inventory_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inventory_logs_id_seq OWNED BY public.inventory_logs.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    title text NOT NULL,
    message text NOT NULL,
    type text DEFAULT 'Eslatma'::text,
    is_read integer DEFAULT 0,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name text NOT NULL,
    category text,
    cost_price numeric DEFAULT 0 NOT NULL,
    sell_price numeric DEFAULT 0 NOT NULL,
    quantity numeric DEFAULT 0 NOT NULL,
    unit text DEFAULT 'dona'::text,
    min_quantity numeric DEFAULT 5,
    note text,
    image_path text,
    barcode text,
    supplier text,
    is_active integer DEFAULT 1,
    dollar_cost numeric DEFAULT 0,
    dollar_price numeric DEFAULT 0,
    exchange_rate numeric DEFAULT 0,
    category_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: sale_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sale_items (
    id integer NOT NULL,
    sale_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity numeric NOT NULL,
    sell_price numeric NOT NULL,
    cost_price numeric NOT NULL,
    subtotal numeric NOT NULL
);


--
-- Name: sale_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sale_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sale_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sale_items_id_seq OWNED BY public.sale_items.id;


--
-- Name: sales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales (
    id integer NOT NULL,
    total_amount numeric DEFAULT 0 NOT NULL,
    total_profit numeric DEFAULT 0 NOT NULL,
    discount numeric DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer,
    car_number text,
    car_model text,
    phone_number text,
    current_km numeric DEFAULT 0,
    next_km numeric DEFAULT 0,
    oil_change_date text,
    next_oil_change_date text,
    notification_date text,
    is_notified integer DEFAULT 0,
    payment_type text DEFAULT 'Naxt'::text,
    bonus_amount numeric DEFAULT 0,
    discount_amount numeric DEFAULT 0,
    cash_amount numeric DEFAULT 0,
    card_amount numeric DEFAULT 0,
    extra_charge numeric DEFAULT 0,
    is_debt integer DEFAULT 0,
    debt_paid integer DEFAULT 0,
    customer_name text,
    customer_phone text
);


--
-- Name: sales_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_id_seq OWNED BY public.sales.id;


--
-- Name: settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.settings (
    id integer NOT NULL,
    key text NOT NULL,
    value text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.settings_id_seq OWNED BY public.settings.id;


--
-- Name: shop_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shop_settings (
    id integer NOT NULL,
    shop_name text DEFAULT 'Moy almashtirish'::text NOT NULL,
    address text,
    phone text,
    logo_path text,
    receipt_footer text,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: shop_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.shop_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: shop_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.shop_settings_id_seq OWNED BY public.shop_settings.id;


--
-- Name: stock_purchases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_purchases (
    id integer NOT NULL,
    product_id integer NOT NULL,
    product_name text,
    quantity numeric NOT NULL,
    unit_cost numeric NOT NULL,
    total_cost numeric NOT NULL,
    dollar_cost numeric DEFAULT 0,
    dollar_price numeric DEFAULT 0,
    exchange_rate numeric DEFAULT 0,
    payment_type text DEFAULT 'Naxt'::text,
    purchase_date text NOT NULL,
    due_date text,
    is_paid integer DEFAULT 0,
    paid_date text,
    remaining_debt numeric DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    firm_id integer,
    CONSTRAINT stock_purchases_payment_type_check CHECK ((payment_type = ANY (ARRAY['Naxt'::text, 'Nasiya'::text])))
);


--
-- Name: stock_purchases_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stock_purchases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stock_purchases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stock_purchases_id_seq OWNED BY public.stock_purchases.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password_hash text NOT NULL,
    role character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'cashier'::character varying])::text[])))
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- Name: backup_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backup_history ALTER COLUMN id SET DEFAULT nextval('public.backup_history_id_seq'::regclass);


--
-- Name: cash_incomes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cash_incomes ALTER COLUMN id SET DEFAULT nextval('public.cash_incomes_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: debt_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.debt_payments ALTER COLUMN id SET DEFAULT nextval('public.debt_payments_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- Name: firm_debt_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firm_debt_payments ALTER COLUMN id SET DEFAULT nextval('public.firm_debt_payments_id_seq'::regclass);


--
-- Name: firm_debts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firm_debts ALTER COLUMN id SET DEFAULT nextval('public.firm_debts_id_seq'::regclass);


--
-- Name: firms id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firms ALTER COLUMN id SET DEFAULT nextval('public.firms_id_seq'::regclass);


--
-- Name: inventory_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_logs ALTER COLUMN id SET DEFAULT nextval('public.inventory_logs_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: sale_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sale_items ALTER COLUMN id SET DEFAULT nextval('public.sale_items_id_seq'::regclass);


--
-- Name: sales id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales ALTER COLUMN id SET DEFAULT nextval('public.sales_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings ALTER COLUMN id SET DEFAULT nextval('public.settings_id_seq'::regclass);


--
-- Name: shop_settings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shop_settings ALTER COLUMN id SET DEFAULT nextval('public.shop_settings_id_seq'::regclass);


--
-- Name: stock_purchases id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_purchases ALTER COLUMN id SET DEFAULT nextval('public.stock_purchases_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.attendance (id, employee_id, check_in, check_out, date) FROM stdin;
\.


--
-- Data for Name: backup_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backup_history (id, backup_date, file_name, file_size, created_by, created_at) FROM stdin;
1	2026-09-03_06-22-45	backup_2026-09-03_06-22-45.sql	34587	1	2026-09-03 06:22:45.79053
\.


--
-- Data for Name: cash_incomes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cash_incomes (id, amount, note, created_at, user_id) FROM stdin;
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (id, name, parent_id, icon, color, created_at) FROM stdin;
1	Moylar	\N	🛢️	#FF6B6B	2026-09-03 01:03:17.662569
2	Filtrlari	\N	🔧	#4ECDC4	2026-09-03 01:03:17.664342
3	Aksessuarlar	\N	🔩	#45B7D1	2026-09-03 01:03:17.665858
\.


--
-- Data for Name: debt_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.debt_payments (id, purchase_id, paid_amount, cash_amount, card_amount, payment_type, paid_date, created_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employees (id, full_name, phone, "position", salary, hire_date, is_active, created_at) FROM stdin;
1	Admin	+998 99 111 22 33	Admin	0	2024-01-01	1	2026-09-03 01:03:17.669458
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.expenses (id, name, amount, category, description, payment_type, created_at, user_id) FROM stdin;
\.


--
-- Data for Name: firm_debt_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.firm_debt_payments (id, debt_id, paid_amount, cash_amount, card_amount, payment_type, paid_date, created_at) FROM stdin;
\.


--
-- Data for Name: firm_debts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.firm_debts (id, firm_id, firm_name, amount, description, debt_type, is_paid, paid_date, created_at) FROM stdin;
\.


--
-- Data for Name: firms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.firms (id, name, phone, address, total_debt, note, created_at) FROM stdin;
1	Test firma	+998 99 123 45 67	Toshkent sh.	0	Test uchun	2026-09-03 01:03:17.667602
\.


--
-- Data for Name: inventory_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventory_logs (id, product_id, action, quantity, created_at, user_id) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, title, message, type, is_read, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (id, name, category, cost_price, sell_price, quantity, unit, min_quantity, note, image_path, barcode, supplier, is_active, dollar_cost, dollar_price, exchange_rate, category_id, created_at) FROM stdin;
\.


--
-- Data for Name: sale_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sale_items (id, sale_id, product_id, quantity, sell_price, cost_price, subtotal) FROM stdin;
\.


--
-- Data for Name: sales; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sales (id, total_amount, total_profit, discount, created_at, user_id, car_number, car_model, phone_number, current_km, next_km, oil_change_date, next_oil_change_date, notification_date, is_notified, payment_type, bonus_amount, discount_amount, cash_amount, card_amount, extra_charge, is_debt, debt_paid, customer_name, customer_phone) FROM stdin;
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.settings (id, key, value, created_at) FROM stdin;
\.


--
-- Data for Name: shop_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.shop_settings (id, shop_name, address, phone, logo_path, receipt_footer, updated_at) FROM stdin;
1	Moy almashtirish	Toshkent sh., ...	+998 99 123 45 67	\N	Rahmat! Xush kelibsiz!	2026-09-03 01:03:17.660308
\.


--
-- Data for Name: stock_purchases; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stock_purchases (id, product_id, product_name, quantity, unit_cost, total_cost, dollar_cost, dollar_price, exchange_rate, payment_type, purchase_date, due_date, is_paid, paid_date, remaining_debt, created_at, firm_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, role, created_at) FROM stdin;
2	cashier	$2b$12$2s9UbN90j0cH5HdTol3yS.aJfEp694htF3TS68K87.NzKKGj7LVbe	cashier	2026-09-03 01:03:17.650087
1	admin	$2b$12$vkm2fjf6m4UcEu/Aq/CH1.vNqN/7CAPMI4KLOlU2ypGv7xImHsgNC	admin	2026-09-03 01:03:17.447644
\.


--
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.attendance_id_seq', 1, false);


--
-- Name: backup_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backup_history_id_seq', 1, true);


--
-- Name: cash_incomes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cash_incomes_id_seq', 1, false);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_id_seq', 3, true);


--
-- Name: debt_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.debt_payments_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employees_id_seq', 1, true);


--
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.expenses_id_seq', 1, false);


--
-- Name: firm_debt_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.firm_debt_payments_id_seq', 1, false);


--
-- Name: firm_debts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.firm_debts_id_seq', 1, false);


--
-- Name: firms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.firms_id_seq', 1, true);


--
-- Name: inventory_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventory_logs_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 1, false);


--
-- Name: sale_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sale_items_id_seq', 1, false);


--
-- Name: sales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sales_id_seq', 1, false);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.settings_id_seq', 1, false);


--
-- Name: shop_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.shop_settings_id_seq', 1, true);


--
-- Name: stock_purchases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_purchases_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- Name: backup_history backup_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backup_history
    ADD CONSTRAINT backup_history_pkey PRIMARY KEY (id);


--
-- Name: cash_incomes cash_incomes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cash_incomes
    ADD CONSTRAINT cash_incomes_pkey PRIMARY KEY (id);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: debt_payments debt_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.debt_payments
    ADD CONSTRAINT debt_payments_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: firm_debt_payments firm_debt_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firm_debt_payments
    ADD CONSTRAINT firm_debt_payments_pkey PRIMARY KEY (id);


--
-- Name: firm_debts firm_debts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firm_debts
    ADD CONSTRAINT firm_debts_pkey PRIMARY KEY (id);


--
-- Name: firms firms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firms
    ADD CONSTRAINT firms_pkey PRIMARY KEY (id);


--
-- Name: inventory_logs inventory_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_logs
    ADD CONSTRAINT inventory_logs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: sale_items sale_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_pkey PRIMARY KEY (id);


--
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- Name: settings settings_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_key_key UNIQUE (key);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: shop_settings shop_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shop_settings
    ADD CONSTRAINT shop_settings_pkey PRIMARY KEY (id);


--
-- Name: stock_purchases stock_purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_purchases
    ADD CONSTRAINT stock_purchases_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: attendance attendance_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: cash_incomes cash_incomes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cash_incomes
    ADD CONSTRAINT cash_incomes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(id);


--
-- Name: debt_payments debt_payments_purchase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.debt_payments
    ADD CONSTRAINT debt_payments_purchase_id_fkey FOREIGN KEY (purchase_id) REFERENCES public.stock_purchases(id);


--
-- Name: expenses expenses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: firm_debt_payments firm_debt_payments_debt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firm_debt_payments
    ADD CONSTRAINT firm_debt_payments_debt_id_fkey FOREIGN KEY (debt_id) REFERENCES public.firm_debts(id);


--
-- Name: firm_debts firm_debts_firm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.firm_debts
    ADD CONSTRAINT firm_debts_firm_id_fkey FOREIGN KEY (firm_id) REFERENCES public.firms(id);


--
-- Name: inventory_logs inventory_logs_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_logs
    ADD CONSTRAINT inventory_logs_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: inventory_logs inventory_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_logs
    ADD CONSTRAINT inventory_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL;


--
-- Name: sale_items sale_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: sale_items sale_items_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id) ON DELETE CASCADE;


--
-- Name: sales sales_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stock_purchases stock_purchases_firm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_purchases
    ADD CONSTRAINT stock_purchases_firm_id_fkey FOREIGN KEY (firm_id) REFERENCES public.firms(id);


--
-- Name: stock_purchases stock_purchases_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_purchases
    ADD CONSTRAINT stock_purchases_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- PostgreSQL database dump complete
--

\unrestrict KysQ3FSFu1H8WNRvkMR1WPm0RWzXuaxHs0c6Qo6IaEIaX0MxJL1oNCefYR6TOsS


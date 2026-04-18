-- =============================================================================
-- CourtAlert Seed Data
-- Run this in NeonDB SQL console or psql
-- Inserts: 2 users + 110 registrations + hearings + sample notifications
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Wipe all existing data
TRUNCATE TABLE whatsapp_commands, notifications, hearings, registrations, users, courts
    RESTART IDENTITY CASCADE;

-- =============================================================================
-- COURTS
-- =============================================================================

INSERT INTO courts (id, state_code, district_code, court_name, address, latitude, longitude, pin_code) VALUES
('c0000001-0000-0000-0000-000000000001', 'MH', 'MUM', 'Bombay High Court', 'Fort, Mumbai, Maharashtra 400032', 18.934719, 72.835023, '400032'),
('c0000001-0000-0000-0000-000000000002', 'DL', 'NDL', 'Delhi High Court', 'Sher Shah Road, New Delhi 110003', 28.623551, 77.240617, '110003'),
('c0000001-0000-0000-0000-000000000003', 'TN', 'CHE', 'Madras High Court', 'High Court Road, Chennai 600104', 13.077244, 80.286499, '600104'),
('c0000001-0000-0000-0000-000000000004', 'UP', 'LKO', 'Allahabad High Court, Lucknow Bench', 'Kaiserbagh, Lucknow 226001', 26.852164, 80.934914, '226001'),
('c0000001-0000-0000-0000-000000000005', 'KA', 'BLR', 'Karnataka High Court', 'Ambedkar Veedhi, Bengaluru 560001', 12.978521, 77.574102, '560001'),
('c0000001-0000-0000-0000-000000000006', 'TS', 'HYD', 'Telangana High Court', 'Nayapul, Hyderabad 500001', 17.385044, 78.486671, '500001'),
('c0000001-0000-0000-0000-000000000007', 'GJ', 'AMD', 'Gujarat High Court', 'Sola, Ahmedabad 380060', 23.052223, 72.580002, '380060'),
('c0000001-0000-0000-0000-000000000008', 'RJ', 'JJP', 'Rajasthan High Court', 'M.I. Road, Jaipur 302005', 26.912434, 75.787271, '302005'),
('c0000001-0000-0000-0000-000000000009', 'MH', 'PNE', 'Pune District Court', 'Shivajinagar, Pune 411005', 18.530209, 73.847694, '411005'),
('c0000001-0000-0000-0000-000000000010', 'UP', 'AGR', 'Agra District Court', 'Belanganj, Agra 282004', 27.176670, 78.008075, '282004');

-- =============================================================================
-- USERS
-- admin@courtalert.in  / Admin@123
-- ngo@legalaid.org     / NGO@123
-- =============================================================================

INSERT INTO users (id, email, hashed_password, full_name, org_name, role, is_active) VALUES
(
    'u0000001-0000-0000-0000-000000000001',
    'admin@courtalert.in',
    crypt('Admin@123', gen_salt('bf', 12)),
    'CourtAlert Admin',
    'CourtAlert',
    'admin',
    TRUE
),
(
    'u0000001-0000-0000-0000-000000000002',
    'ngo@legalaid.org',
    crypt('NGO@123', gen_salt('bf', 12)),
    'Ravi Kumar',
    'Legal Aid Society Mumbai',
    'ngo_user',
    TRUE
);

-- =============================================================================
-- REGISTRATIONS (110 cases)
-- Spread across states, languages, case types
-- =============================================================================

INSERT INTO registrations (id, cnr_number, phone_number, language, case_title, court_name, state_code, district_code, is_active, last_synced_at, registered_by) VALUES
-- Maharashtra / Hindi + Marathi (30 cases)
('r0000001-0000-0000-0000-000000000001','MHMUM010001232023','+919876540001','hi','Sharma vs State of Maharashtra','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '1 day','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000002','MHMUM010002342023','+919876540002','mr','Patil vs Patil','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '2 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000003','MHMUM010003452023','+919876540003','hi','Desai vs Municipal Corporation of Mumbai','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '3 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000004','MHMUM010004562023','+919876540004','mr','Joshi vs Joshi','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '4 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000005','MHMUM010005672023','+919876540005','hi','Kulkarni vs Income Tax Department','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '5 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000006','MHPNE010006782023','+919876540006','mr','More vs State of Maharashtra','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '6 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000007','MHPNE010007892023','+919876540007','mr','Bhosale vs Bhosale','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '7 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000008','MHPNE010008902023','+919876540008','hi','Shinde vs Collector Pune','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '8 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000009','MHMUM010009012022','+919876540009','mr','Gaikwad vs Reserve Bank of India','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '9 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000010','MHMUM010010122022','+919876540010','hi','Thakur vs Thakur','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '10 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000011','MHMUM010011232022','+919876540011','mr','Pawar vs State Bank of India','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '11 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000012','MHMUM010012342022','+919876540012','hi','Naik vs Naik','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '12 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000013','MHPNE010013452022','+919876540013','mr','Sawant vs Sawant','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '13 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000014','MHPNE010014562022','+919876540014','hi','Wagh vs MSEB','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '14 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000015','MHMUM010015672022','+919876540015','mr','Chavan vs Union of India','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '15 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000016','MHMUM010016782022','+919876540016','hi','Deshpande vs Deshpande','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '16 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000017','MHMUM010017892022','+919876540017','mr','Rane vs Maharashtra Housing Board','Bombay High Court, Mumbai','MH','MUM',FALSE,NOW() - INTERVAL '60 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000018','MHPNE010018902022','+919876540018','hi','Kadam vs Kadam','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '17 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000019','MHPNE010019012021','+919876540019','mr','Mane vs State of Maharashtra','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '18 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000020','MHMUM010020122021','+919876540020','hi','Salvi vs Income Tax Department','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '19 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000021','MHMUM010021232021','+919876540021','mr','Kale vs Kale','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '20 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000022','MHMUM010022342021','+919876540022','hi','Jadhav vs Mumbai Port Trust','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '21 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000023','MHPNE010023452021','+919876540023','mr','Kamble vs Collector','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '22 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000024','MHPNE010024562021','+919876540024','hi','Waghmare vs State of Maharashtra','Pune District Court','MH','PNE',FALSE,NOW() - INTERVAL '90 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000025','MHMUM010025672021','+919876540025','mr','Lokhande vs Union of India','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '23 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000026','MHMUM010026782021','+919876540026','hi','Shirke vs MHADA','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '24 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000027','MHMUM010027892021','+919876540027','mr','Gavhane vs Gavhane','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '25 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000028','MHPNE010028902020','+919876540028','hi','Talekar vs State of Maharashtra','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '26 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000029','MHPNE010029012020','+919876540029','mr','Bhalerao vs Municipal Council Pune','Pune District Court','MH','PNE',TRUE,NOW() - INTERVAL '27 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000030','MHMUM010030122020','+919876540030','hi','Ghuge vs Union of India','Bombay High Court, Mumbai','MH','MUM',TRUE,NOW() - INTERVAL '28 days','u0000001-0000-0000-0000-000000000002'),

-- Delhi / Hindi (20 cases)
('r0000001-0000-0000-0000-000000000031','DLNDL010001232023','+919876541001','hi','Kumar vs Union of India','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '1 day','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000032','DLNDL010002342023','+919876541002','hi','Singh vs Delhi Development Authority','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '2 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000033','DLNDL010003452023','+919876541003','hi','Verma vs Verma','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '3 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000034','DLNDL010004562023','+919876541004','hi','Gupta vs Central Government','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '4 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000035','DLNDL010005672023','+919876541005','hi','Mishra vs Income Tax Department','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '5 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000036','DLNDL010006782022','+919876541006','hi','Yadav vs Delhi Police','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '6 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000037','DLNDL010007892022','+919876541007','hi','Pandey vs Pandey','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '7 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000038','DLNDL010008902022','+919876541008','hi','Tiwari vs Municipal Corporation of Delhi','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '8 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000039','DLNDL010009012022','+919876541009','hi','Dubey vs Union of India','Delhi High Court, New Delhi','DL','NDL',FALSE,NOW() - INTERVAL '75 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000040','DLNDL010010122022','+919876541010','hi','Chauhan vs Chauhan','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '9 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000041','DLNDL010011232021','+919876541011','hi','Rawat vs Delhi Jal Board','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '10 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000042','DLNDL010012342021','+919876541012','hi','Bisht vs State of Delhi','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '11 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000043','DLNDL010013452021','+919876541013','hi','Negi vs NDMC','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '12 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000044','DLNDL010014562021','+919876541014','hi','Arora vs Arora','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '13 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000045','DLNDL010015672021','+919876541015','hi','Kapoor vs Union of India','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '14 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000046','DLNDL010016782021','+919876541016','hi','Malhotra vs Malhotra','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '15 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000047','DLNDL010017892020','+919876541017','hi','Batra vs Delhi Transport Corporation','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '16 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000048','DLNDL010018902020','+919876541018','hi','Khanna vs Income Tax Department','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '17 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000049','DLNDL010019012020','+919876541019','hi','Luthra vs Union of India','Delhi High Court, New Delhi','DL','NDL',TRUE,NOW() - INTERVAL '18 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000050','DLNDL010020122020','+919876541020','hi','Mehra vs Mehra','Delhi High Court, New Delhi','DL','NDL',FALSE,NOW() - INTERVAL '120 days','u0000001-0000-0000-0000-000000000002'),

-- Tamil Nadu / Tamil (20 cases)
('r0000001-0000-0000-0000-000000000051','TNCHE010001232023','+919876542001','ta','Murugan vs Government of Tamil Nadu','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '1 day','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000052','TNCHE010002342023','+919876542002','ta','Rajan vs Tamil Nadu Housing Board','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '2 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000053','TNCHE010003452023','+919876542003','ta','Selvam vs Selvam','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '3 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000054','TNCHE010004562023','+919876542004','ta','Arumugam vs State of Tamil Nadu','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '4 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000055','TNCHE010005672023','+919876542005','ta','Suresh vs Chennai Metropolitan Authority','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '5 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000056','TNCHE010006782022','+919876542006','ta','Krishnan vs Krishnan','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '6 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000057','TNCHE010007892022','+919876542007','ta','Venkatesh vs Income Tax Department','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '7 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000058','TNCHE010008902022','+919876542008','ta','Annamalai vs Union of India','Madras High Court, Chennai','TN','CHE',FALSE,NOW() - INTERVAL '80 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000059','TNCHE010009012022','+919876542009','ta','Sundaram vs State of Tamil Nadu','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '8 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000060','TNCHE010010122022','+919876542010','ta','Palanisamy vs Palanisamy','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '9 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000061','TNCHE010011232021','+919876542011','ta','Govindasamy vs Tamil Nadu Electricity Board','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '10 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000062','TNCHE010012342021','+919876542012','ta','Natarajan vs State of Tamil Nadu','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '11 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000063','TNCHE010013452021','+919876542013','ta','Subramanian vs Subramanian','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '12 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000064','TNCHE010014562021','+919876542014','ta','Thangavel vs Collector Chennai','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '13 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000065','TNCHE010015672021','+919876542015','ta','Ramasamy vs Union of India','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '14 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000066','TNCHE010016782020','+919876542016','ta','Muthusamy vs Muthusamy','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '15 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000067','TNCHE010017892020','+919876542017','ta','Durai vs State of Tamil Nadu','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '16 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000068','TNCHE010018902020','+919876542018','ta','Pandian vs Tamil Nadu Water Supply Board','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '17 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000069','TNCHE010019012019','+919876542019','ta','Kandasamy vs Kandasamy','Madras High Court, Chennai','TN','CHE',FALSE,NOW() - INTERVAL '100 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000070','TNCHE010020122019','+919876542020','ta','Periyasamy vs Government of Tamil Nadu','Madras High Court, Chennai','TN','CHE',TRUE,NOW() - INTERVAL '18 days','u0000001-0000-0000-0000-000000000002'),

-- Karnataka / Kannada (15 cases)
('r0000001-0000-0000-0000-000000000071','KABLR010001232023','+919876543001','kn','Reddy vs State of Karnataka','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '1 day','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000072','KABLR010002342023','+919876543002','kn','Gowda vs Bruhat Bengaluru Mahanagara Palike','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '2 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000073','KABLR010003452023','+919876543003','kn','Naidu vs Naidu','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '3 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000074','KABLR010004562022','+919876543004','kn','Rao vs Karnataka Housing Board','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '4 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000075','KABLR010005672022','+919876543005','kn','Hegde vs Union of India','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '5 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000076','KABLR010006782022','+919876543006','kn','Shetty vs State of Karnataka','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '6 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000077','KABLR010007892021','+919876543007','kn','Bhat vs Bhat','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '7 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000078','KABLR010008902021','+919876543008','kn','Kamath vs Karnataka Electricity Board','Karnataka High Court, Bengaluru','KA','BLR',FALSE,NOW() - INTERVAL '70 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000079','KABLR010009012021','+919876543009','kn','Nair vs Nair','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '8 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000080','KABLR010010122021','+919876543010','kn','Iyer vs State of Karnataka','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '9 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000081','KABLR010011232020','+919876543011','kn','Krishnamurthy vs Krishnamurthy','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '10 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000082','KABLR010012342020','+919876543012','kn','Venkataramu vs Union of India','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '11 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000083','KABLR010013452020','+919876543013','kn','Devaraju vs Collector Bengaluru','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '12 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000084','KABLR010014562019','+919876543014','kn','Subbaiah vs Karnataka Road Development Corporation','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '13 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000085','KABLR010015672019','+919876543015','kn','Ramaiah vs Ramaiah','Karnataka High Court, Bengaluru','KA','BLR',TRUE,NOW() - INTERVAL '14 days','u0000001-0000-0000-0000-000000000002'),

-- Telangana / Telugu (10 cases)
('r0000001-0000-0000-0000-000000000086','TSHYD010001232023','+919876544001','te','Reddy vs State of Telangana','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '1 day','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000087','TSHYD010002342023','+919876544002','te','Rao vs TSRTC','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '2 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000088','TSHYD010003452022','+919876544003','te','Naidu vs Naidu','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '3 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000089','TSHYD010004562022','+919876544004','te','Sharma vs Government of Telangana','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '4 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000090','TSHYD010005672021','+919876544005','te','Krishnarao vs Krishnarao','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '5 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000091','TSHYD010006782021','+919876544006','te','Venkataramana vs Union of India','Telangana High Court, Hyderabad','TS','HYD',FALSE,NOW() - INTERVAL '65 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000092','TSHYD010007892021','+919876544007','te','Prasad vs HMDA','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '6 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000093','TSHYD010008902020','+919876544008','te','Subrahmanyam vs State of Telangana','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '7 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000094','TSHYD010009012020','+919876544009','te','Apparao vs Apparao','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '8 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000095','TSHYD010010122020','+919876544010','te','Laxminarayana vs Collector Hyderabad','Telangana High Court, Hyderabad','TS','HYD',TRUE,NOW() - INTERVAL '9 days','u0000001-0000-0000-0000-000000000002'),

-- Uttar Pradesh / Hindi (15 cases)
('r0000001-0000-0000-0000-000000000096','UPLKO010001232023','+919876545001','hi','Yadav vs State of Uttar Pradesh','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '1 day','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000097','UPLKO010002342023','+919876545002','hi','Maurya vs Lucknow Development Authority','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '2 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000098','UPLKO010003452023','+919876545003','hi','Tripathi vs Tripathi','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '3 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000099','UPLKO010004562022','+919876545004','hi','Shukla vs Income Tax Department','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '4 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000100','UPLKO010005672022','+919876545005','hi','Dwivedi vs Union of India','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '5 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000101','UPLKO010006782022','+919876545006','hi','Pandey vs Pandey','Allahabad High Court, Lucknow Bench','UP','LKO',FALSE,NOW() - INTERVAL '55 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000102','ULAGR010007892022','+919876545007','hi','Saxena vs Agra Development Authority','Agra District Court','UP','AGR',TRUE,NOW() - INTERVAL '6 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000103','ULAGR010008902021','+919876545008','hi','Srivastava vs Srivastava','Agra District Court','UP','AGR',TRUE,NOW() - INTERVAL '7 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000104','ULAGR010009012021','+919876545009','hi','Agarwal vs State of Uttar Pradesh','Agra District Court','UP','AGR',TRUE,NOW() - INTERVAL '8 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000105','ULAGR010010122021','+919876545010','hi','Bansal vs UP Jal Nigam','Agra District Court','UP','AGR',TRUE,NOW() - INTERVAL '9 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000106','UPLKO010011232021','+919876545011','hi','Chaturvedi vs Union of India','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '10 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000107','UPLKO010012342020','+919876545012','hi','Bajpai vs Bajpai','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '11 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000108','UPLKO010013452020','+919876545013','hi','Misra vs Collector Lucknow','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '12 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000109','UPLKO010014562020','+919876545014','hi','Pathak vs State of Uttar Pradesh','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '13 days','u0000001-0000-0000-0000-000000000002'),
('r0000001-0000-0000-0000-000000000110','UPLKO010015672019','+919876545015','hi','Upadhyay vs Upadhyay','Allahabad High Court, Lucknow Bench','UP','LKO',TRUE,NOW() - INTERVAL '14 days','u0000001-0000-0000-0000-000000000002');

-- =============================================================================
-- HEARINGS (2 hearings per registration)
-- One past (completed), one upcoming
-- For first 10 registrations: upcoming hearing is TODAY+7 so alerts fire immediately
-- =============================================================================

INSERT INTO hearings (registration_id, hearing_date, hearing_type, court_room, judge_name, purpose, is_completed) VALUES
-- First 10 registrations: upcoming in 7 days (alerts will fire on next CRON run)
('r0000001-0000-0000-0000-000000000001', CURRENT_DATE - 45, 'First Hearing',   'Court Room 1',  'Hon. Justice A.K. Mehta',      'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000001', CURRENT_DATE + 7,  'Final Arguments', 'Court Room 1',  'Hon. Justice A.K. Mehta',      'Final arguments on merits',  FALSE),
('r0000001-0000-0000-0000-000000000002', CURRENT_DATE - 30, 'First Hearing',   'Court Room 2',  'Hon. Justice B.N. Srikrishna', 'Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000002', CURRENT_DATE + 7,  'IA Hearing',      'Court Room 2',  'Hon. Justice B.N. Srikrishna', 'Hearing on interim relief',  FALSE),
('r0000001-0000-0000-0000-000000000003', CURRENT_DATE - 60, 'Admission',       'Court Room 3',  'Hon. Justice P.B. Sawant',     'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000003', CURRENT_DATE + 7,  'Evidence',        'Court Room 3',  'Hon. Justice P.B. Sawant',     'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000004', CURRENT_DATE - 20, 'First Hearing',   'Court Room 4',  'Hon. Justice R.M. Lodha',      'Initial pleadings',          TRUE),
('r0000001-0000-0000-0000-000000000004', CURRENT_DATE + 7,  'Written Statement','Court Room 4', 'Hon. Justice R.M. Lodha',      'Filing written statement',   FALSE),
('r0000001-0000-0000-0000-000000000005', CURRENT_DATE - 15, 'Admission',       'Court Room 5',  'Hon. Justice H.L. Dattu',      'Hearing on admissibility',   TRUE),
('r0000001-0000-0000-0000-000000000005', CURRENT_DATE + 7,  'Arguments',       'Court Room 5',  'Hon. Justice H.L. Dattu',      'Arguments on main matter',   FALSE),
('r0000001-0000-0000-0000-000000000006', CURRENT_DATE - 25, 'First Hearing',   'Court Room 6',  'Hon. Justice V.S. Sirpurkar',  'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000006', CURRENT_DATE + 7,  'IA Hearing',      'Court Room 6',  'Hon. Justice V.S. Sirpurkar',  'Interim application',        FALSE),
('r0000001-0000-0000-0000-000000000007', CURRENT_DATE - 40, 'Mediation',       'Court Room 7',  'Hon. Justice S.B. Sinha',      'Court-ordered mediation',    TRUE),
('r0000001-0000-0000-0000-000000000007', CURRENT_DATE + 7,  'Final Arguments', 'Court Room 7',  'Hon. Justice S.B. Sinha',      'Final arguments',            FALSE),
('r0000001-0000-0000-0000-000000000008', CURRENT_DATE - 10, 'First Hearing',   'Court Room 8',  'Hon. Justice G.S. Singhvi',    'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000008', CURRENT_DATE + 7,  'Evidence',        'Court Room 8',  'Hon. Justice G.S. Singhvi',    'Examination of witnesses',   FALSE),
('r0000001-0000-0000-0000-000000000009', CURRENT_DATE - 50, 'Admission',       'Court Room 9',  'Hon. Justice A.K. Ganguly',    'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000009', CURRENT_DATE + 7,  'Arguments',       'Court Room 9',  'Hon. Justice A.K. Ganguly',    'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000010', CURRENT_DATE - 35, 'First Hearing',   'Court Room 10', 'Hon. Justice D.K. Jain',       'Filing of reply',            TRUE),
('r0000001-0000-0000-0000-000000000010', CURRENT_DATE + 7,  'Final Arguments', 'Court Room 10', 'Hon. Justice D.K. Jain',       'Final hearing',              FALSE),

-- Remaining registrations: spread over 14 to 60 days upcoming
('r0000001-0000-0000-0000-000000000011', CURRENT_DATE - 30, 'First Hearing',   'Court Room 1',  'Hon. Justice A.K. Mehta',      'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000011', CURRENT_DATE + 14, 'Arguments',       'Court Room 1',  'Hon. Justice A.K. Mehta',      'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000012', CURRENT_DATE - 20, 'Admission',       'Court Room 2',  'Hon. Justice B.N. Srikrishna', 'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000012', CURRENT_DATE + 14, 'Evidence',        'Court Room 2',  'Hon. Justice B.N. Srikrishna', 'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000013', CURRENT_DATE - 45, 'First Hearing',   'Court Room 3',  'Hon. Justice P.B. Sawant',     'Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000013', CURRENT_DATE + 21, 'IA Hearing',      'Court Room 3',  'Hon. Justice P.B. Sawant',     'Interim application',        FALSE),
('r0000001-0000-0000-0000-000000000014', CURRENT_DATE - 15, 'Admission',       'Court Room 4',  'Hon. Justice R.M. Lodha',      'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000014', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 4',  'Hon. Justice R.M. Lodha',      'Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000015', CURRENT_DATE - 60, 'First Hearing',   'Court Room 5',  'Hon. Justice H.L. Dattu',      'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000015', CURRENT_DATE + 30, 'Arguments',       'Court Room 5',  'Hon. Justice H.L. Dattu',      'Final arguments',            FALSE),
('r0000001-0000-0000-0000-000000000016', CURRENT_DATE - 25, 'First Hearing',   'Court Room 6',  'Hon. Justice V.S. Sirpurkar',  'Filing of pleadings',        TRUE),
('r0000001-0000-0000-0000-000000000016', CURRENT_DATE + 30, 'Evidence',        'Court Room 6',  'Hon. Justice V.S. Sirpurkar',  'Cross examination',          FALSE),
('r0000001-0000-0000-0000-000000000018', CURRENT_DATE - 30, 'First Hearing',   'Court Room 8',  'Hon. Justice G.S. Singhvi',    'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000018', CURRENT_DATE + 14, 'Arguments',       'Court Room 8',  'Hon. Justice G.S. Singhvi',    'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000019', CURRENT_DATE - 40, 'Admission',       'Court Room 9',  'Hon. Justice A.K. Ganguly',    'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000019', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 9',  'Hon. Justice A.K. Ganguly',    'Final hearing',              FALSE),
('r0000001-0000-0000-0000-000000000020', CURRENT_DATE - 20, 'First Hearing',   'Court Room 10', 'Hon. Justice D.K. Jain',       'Initial pleadings',          TRUE),
('r0000001-0000-0000-0000-000000000020', CURRENT_DATE + 30, 'Evidence',        'Court Room 10', 'Hon. Justice D.K. Jain',       'Evidence recording',         FALSE),
('r0000001-0000-0000-0000-000000000021', CURRENT_DATE - 35, 'First Hearing',   'Court Room 1',  'Hon. Justice A.K. Mehta',      'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000021', CURRENT_DATE + 45, 'Arguments',       'Court Room 1',  'Hon. Justice A.K. Mehta',      'Final arguments',            FALSE),
('r0000001-0000-0000-0000-000000000022', CURRENT_DATE - 50, 'Admission',       'Court Room 2',  'Hon. Justice B.N. Srikrishna', 'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000022', CURRENT_DATE + 45, 'IA Hearing',      'Court Room 2',  'Hon. Justice B.N. Srikrishna', 'Interim application',        FALSE),
('r0000001-0000-0000-0000-000000000023', CURRENT_DATE - 15, 'First Hearing',   'Court Room 3',  'Hon. Justice P.B. Sawant',     'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000023', CURRENT_DATE + 60, 'Final Arguments', 'Court Room 3',  'Hon. Justice P.B. Sawant',     'Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000025', CURRENT_DATE - 25, 'First Hearing',   'Court Room 5',  'Hon. Justice H.L. Dattu',      'Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000025', CURRENT_DATE + 14, 'Evidence',        'Court Room 5',  'Hon. Justice H.L. Dattu',      'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000026', CURRENT_DATE - 60, 'Admission',       'Court Room 6',  'Hon. Justice V.S. Sirpurkar',  'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000026', CURRENT_DATE + 21, 'Arguments',       'Court Room 6',  'Hon. Justice V.S. Sirpurkar',  'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000027', CURRENT_DATE - 30, 'First Hearing',   'Court Room 7',  'Hon. Justice S.B. Sinha',      'Initial pleadings',          TRUE),
('r0000001-0000-0000-0000-000000000027', CURRENT_DATE + 30, 'Final Arguments', 'Court Room 7',  'Hon. Justice S.B. Sinha',      'Final hearing',              FALSE),
('r0000001-0000-0000-0000-000000000028', CURRENT_DATE - 45, 'First Hearing',   'Court Room 8',  'Hon. Justice G.S. Singhvi',    'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000028', CURRENT_DATE + 45, 'Evidence',        'Court Room 8',  'Hon. Justice G.S. Singhvi',    'Cross examination',          FALSE),
('r0000001-0000-0000-0000-000000000029', CURRENT_DATE - 20, 'Admission',       'Court Room 9',  'Hon. Justice A.K. Ganguly',    'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000029', CURRENT_DATE + 60, 'Arguments',       'Court Room 9',  'Hon. Justice A.K. Ganguly',    'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000030', CURRENT_DATE - 35, 'First Hearing',   'Court Room 10', 'Hon. Justice D.K. Jain',       'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000030', CURRENT_DATE + 14, 'Final Arguments', 'Court Room 10', 'Hon. Justice D.K. Jain',       'Final hearing',              FALSE),
-- Delhi cases
('r0000001-0000-0000-0000-000000000031', CURRENT_DATE - 30, 'First Hearing',   'Court Room 1',  'Hon. Justice S.H. Kapadia',    'Filing of pleadings',        TRUE),
('r0000001-0000-0000-0000-000000000031', CURRENT_DATE + 7,  'Arguments',       'Court Room 1',  'Hon. Justice S.H. Kapadia',    'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000032', CURRENT_DATE - 20, 'Admission',       'Court Room 2',  'Hon. Justice K.G. Balakrishnan','Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000032', CURRENT_DATE + 14, 'Evidence',        'Court Room 2',  'Hon. Justice K.G. Balakrishnan','Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000033', CURRENT_DATE - 45, 'First Hearing',   'Court Room 3',  'Hon. Justice Y.K. Sabharwal',  'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000033', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 3',  'Hon. Justice Y.K. Sabharwal',  'Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000034', CURRENT_DATE - 15, 'First Hearing',   'Court Room 4',  'Hon. Justice R.C. Lahoti',     'Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000034', CURRENT_DATE + 30, 'IA Hearing',      'Court Room 4',  'Hon. Justice R.C. Lahoti',     'Interim application',        FALSE),
('r0000001-0000-0000-0000-000000000035', CURRENT_DATE - 60, 'Admission',       'Court Room 5',  'Hon. Justice V.N. Khare',      'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000035', CURRENT_DATE + 45, 'Arguments',       'Court Room 5',  'Hon. Justice V.N. Khare',      'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000036', CURRENT_DATE - 25, 'First Hearing',   'Court Room 6',  'Hon. Justice B.N. Agrawal',    'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000036', CURRENT_DATE + 14, 'Evidence',        'Court Room 6',  'Hon. Justice B.N. Agrawal',    'Evidence recording',         FALSE),
('r0000001-0000-0000-0000-000000000037', CURRENT_DATE - 35, 'First Hearing',   'Court Room 7',  'Hon. Justice S.B. Sinha',      'Initial pleadings',          TRUE),
('r0000001-0000-0000-0000-000000000037', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 7',  'Hon. Justice S.B. Sinha',      'Final hearing',              FALSE),
('r0000001-0000-0000-0000-000000000038', CURRENT_DATE - 50, 'Admission',       'Court Room 8',  'Hon. Justice A.R. Lakshmanan', 'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000038', CURRENT_DATE + 30, 'Arguments',       'Court Room 8',  'Hon. Justice A.R. Lakshmanan', 'Final arguments',            FALSE),
('r0000001-0000-0000-0000-000000000040', CURRENT_DATE - 20, 'First Hearing',   'Court Room 10', 'Hon. Justice D.K. Jain',       'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000040', CURRENT_DATE + 45, 'Evidence',        'Court Room 10', 'Hon. Justice D.K. Jain',       'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000041', CURRENT_DATE - 30, 'Admission',       'Court Room 1',  'Hon. Justice S.H. Kapadia',    'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000041', CURRENT_DATE + 14, 'Arguments',       'Court Room 1',  'Hon. Justice S.H. Kapadia',    'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000042', CURRENT_DATE - 45, 'First Hearing',   'Court Room 2',  'Hon. Justice K.G. Balakrishnan','Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000042', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 2',  'Hon. Justice K.G. Balakrishnan','Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000043', CURRENT_DATE - 15, 'First Hearing',   'Court Room 3',  'Hon. Justice Y.K. Sabharwal',  'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000043', CURRENT_DATE + 30, 'IA Hearing',      'Court Room 3',  'Hon. Justice Y.K. Sabharwal',  'Interim application',        FALSE),
-- Tamil Nadu cases
('r0000001-0000-0000-0000-000000000051', CURRENT_DATE - 30, 'First Hearing',   'Court Room 1',  'Hon. Justice S. Ramaswamy',    'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000051', CURRENT_DATE + 7,  'Arguments',       'Court Room 1',  'Hon. Justice S. Ramaswamy',    'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000052', CURRENT_DATE - 20, 'Admission',       'Court Room 2',  'Hon. Justice K. Venkataswami', 'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000052', CURRENT_DATE + 14, 'Evidence',        'Court Room 2',  'Hon. Justice K. Venkataswami', 'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000053', CURRENT_DATE - 45, 'First Hearing',   'Court Room 3',  'Hon. Justice M. Jagannadha Rao','Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000053', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 3',  'Hon. Justice M. Jagannadha Rao','Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000054', CURRENT_DATE - 15, 'Admission',       'Court Room 4',  'Hon. Justice S.S.M. Quadri',   'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000054', CURRENT_DATE + 30, 'Arguments',       'Court Room 4',  'Hon. Justice S.S.M. Quadri',   'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000055', CURRENT_DATE - 60, 'First Hearing',   'Court Room 5',  'Hon. Justice R.P. Sethi',      'Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000055', CURRENT_DATE + 45, 'IA Hearing',      'Court Room 5',  'Hon. Justice R.P. Sethi',      'Interim application',        FALSE),
('r0000001-0000-0000-0000-000000000056', CURRENT_DATE - 25, 'First Hearing',   'Court Room 6',  'Hon. Justice D.P. Wadhwa',     'Filing of pleadings',        TRUE),
('r0000001-0000-0000-0000-000000000056', CURRENT_DATE + 14, 'Evidence',        'Court Room 6',  'Hon. Justice D.P. Wadhwa',     'Cross examination',          FALSE),
('r0000001-0000-0000-0000-000000000057', CURRENT_DATE - 35, 'Admission',       'Court Room 7',  'Hon. Justice M.B. Shah',       'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000057', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 7',  'Hon. Justice M.B. Shah',       'Final hearing',              FALSE),
-- Karnataka cases
('r0000001-0000-0000-0000-000000000071', CURRENT_DATE - 30, 'First Hearing',   'Court Room 1',  'Hon. Justice Y.V. Chandrachud','Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000071', CURRENT_DATE + 7,  'Arguments',       'Court Room 1',  'Hon. Justice Y.V. Chandrachud','Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000072', CURRENT_DATE - 20, 'Admission',       'Court Room 2',  'Hon. Justice P.N. Bhagwati',   'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000072', CURRENT_DATE + 14, 'Evidence',        'Court Room 2',  'Hon. Justice P.N. Bhagwati',   'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000073', CURRENT_DATE - 45, 'First Hearing',   'Court Room 3',  'Hon. Justice V.R. Krishna Iyer','Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000073', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 3',  'Hon. Justice V.R. Krishna Iyer','Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000074', CURRENT_DATE - 15, 'Admission',       'Court Room 4',  'Hon. Justice H.R. Khanna',     'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000074', CURRENT_DATE + 30, 'Arguments',       'Court Room 4',  'Hon. Justice H.R. Khanna',     'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000075', CURRENT_DATE - 60, 'First Hearing',   'Court Room 5',  'Hon. Justice K. Subba Rao',    'Preliminary hearing',        TRUE),
('r0000001-0000-0000-0000-000000000075', CURRENT_DATE + 45, 'IA Hearing',      'Court Room 5',  'Hon. Justice K. Subba Rao',    'Interim application',        FALSE),
-- Telangana cases
('r0000001-0000-0000-0000-000000000086', CURRENT_DATE - 30, 'First Hearing',   'Court Room 1',  'Hon. Justice T.L. Venkatarama Aiyar','Filing of documents', TRUE),
('r0000001-0000-0000-0000-000000000086', CURRENT_DATE + 7,  'Arguments',       'Court Room 1',  'Hon. Justice T.L. Venkatarama Aiyar','Arguments on merits',FALSE),
('r0000001-0000-0000-0000-000000000087', CURRENT_DATE - 20, 'Admission',       'Court Room 2',  'Hon. Justice N.H. Bhagwati',   'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000087', CURRENT_DATE + 14, 'Evidence',        'Court Room 2',  'Hon. Justice N.H. Bhagwati',   'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000088', CURRENT_DATE - 45, 'First Hearing',   'Court Room 3',  'Hon. Justice G.J. Chagla',     'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000088', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 3',  'Hon. Justice G.J. Chagla',     'Final hearing on merits',    FALSE),
-- Uttar Pradesh cases
('r0000001-0000-0000-0000-000000000096', CURRENT_DATE - 30, 'First Hearing',   'Court Room 1',  'Hon. Justice B.P. Sinha',      'Filing of pleadings',        TRUE),
('r0000001-0000-0000-0000-000000000096', CURRENT_DATE + 7,  'Arguments',       'Court Room 1',  'Hon. Justice B.P. Sinha',      'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000097', CURRENT_DATE - 20, 'Admission',       'Court Room 2',  'Hon. Justice S.R. Das',        'Admission hearing',          TRUE),
('r0000001-0000-0000-0000-000000000097', CURRENT_DATE + 14, 'Evidence',        'Court Room 2',  'Hon. Justice S.R. Das',        'Recording of evidence',      FALSE),
('r0000001-0000-0000-0000-000000000098', CURRENT_DATE - 45, 'First Hearing',   'Court Room 3',  'Hon. Justice M.C. Mahajan',    'Initial appearance',         TRUE),
('r0000001-0000-0000-0000-000000000098', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 3',  'Hon. Justice M.C. Mahajan',    'Final hearing on merits',    FALSE),
('r0000001-0000-0000-0000-000000000099', CURRENT_DATE - 15, 'Admission',       'Court Room 4',  'Hon. Justice H.J. Kania',      'Admission of petition',      TRUE),
('r0000001-0000-0000-0000-000000000099', CURRENT_DATE + 30, 'Arguments',       'Court Room 4',  'Hon. Justice H.J. Kania',      'Arguments on merits',        FALSE),
('r0000001-0000-0000-0000-000000000100', CURRENT_DATE - 60, 'First Hearing',   'Court Room 5',  'Hon. Justice P.B. Gajendragadkar','Preliminary hearing',      TRUE),
('r0000001-0000-0000-0000-000000000100', CURRENT_DATE + 45, 'IA Hearing',      'Court Room 5',  'Hon. Justice P.B. Gajendragadkar','Interim application',      FALSE),
('r0000001-0000-0000-0000-000000000102', CURRENT_DATE - 25, 'First Hearing',   'Court Room 6',  'Hon. Justice A.K. Sarkar',     'Filing of documents',        TRUE),
('r0000001-0000-0000-0000-000000000102', CURRENT_DATE + 14, 'Evidence',        'Court Room 6',  'Hon. Justice A.K. Sarkar',     'Evidence recording',         FALSE),
('r0000001-0000-0000-0000-000000000103', CURRENT_DATE - 35, 'Admission',       'Court Room 7',  'Hon. Justice T.L. Venkatarama Aiyar','Admission hearing',     TRUE),
('r0000001-0000-0000-0000-000000000103', CURRENT_DATE + 21, 'Final Arguments', 'Court Room 7',  'Hon. Justice T.L. Venkatarama Aiyar','Final hearing',          FALSE);

-- =============================================================================
-- SAMPLE NOTIFICATIONS (for registrations 1-10, past 7-day reminders already sent)
-- =============================================================================

INSERT INTO notifications (registration_id, hearing_id, channel, status, message_text, message_language, days_before, twilio_sid, sent_at, delivered_at)
SELECT
    r.id,
    h.id,
    'sms'::channel_type,
    'delivered'::notification_status,
    '⚖️ CourtAlert: आपके केस ' || r.case_title || ' की सुनवाई 7 दिन बाद है। तारीख: ' || TO_CHAR(h.hearing_date, 'DD Mon YYYY'),
    r.language,
    7,
    'SM' || UPPER(SUBSTRING(MD5(r.id::text || h.id::text), 1, 32)),
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '23 hours'
FROM registrations r
JOIN hearings h ON h.registration_id = r.id
WHERE r.id IN (
    'r0000001-0000-0000-0000-000000000001',
    'r0000001-0000-0000-0000-000000000002',
    'r0000001-0000-0000-0000-000000000003',
    'r0000001-0000-0000-0000-000000000004',
    'r0000001-0000-0000-0000-000000000005'
)
AND h.is_completed = FALSE;

-- =============================================================================
-- SAMPLE WHATSAPP COMMANDS
-- =============================================================================

INSERT INTO whatsapp_commands (from_number, body, command_type, cnr_extracted, language_extracted, response_sent, received_at) VALUES
('+919876540001', 'REG MHMUM010001232023 HI', 'REG',     'MHMUM010001232023', 'hi', '✅ Registered successfully!', NOW() - INTERVAL '5 days'),
('+919876540010', 'STATUS',                   'STATUS',  NULL,                NULL, '📋 You have 1 active case(s)', NOW() - INTERVAL '3 days'),
('+919876541001', 'REG DLNDL010001232023 HI', 'REG',     'DLNDL010001232023', 'hi', '✅ Registered successfully!', NOW() - INTERVAL '2 days'),
('+919876542001', 'STATUS',                   'STATUS',  NULL,                NULL, '📋 You have 1 active case(s)', NOW() - INTERVAL '1 day'),
('+919876540017', 'STOP',                     'STOP',    NULL,                NULL, '✅ Unsubscribed. 1 case(s) deactivated.', NOW() - INTERVAL '60 days'),
('+919999999999', 'hello',                    'UNKNOWN', NULL,                NULL, '👋 Welcome to CourtAlert!',   NOW() - INTERVAL '4 days');

-- =============================================================================
-- SUMMARY
-- =============================================================================
-- Users:         2  (admin@courtalert.in / Admin@123, ngo@legalaid.org / NGO@123)
-- Courts:        10
-- Registrations: 110 (100 active, 10 inactive/deactivated)
-- Hearings:      ~180 (2 per registration for majority)
-- Notifications: 5 sample delivered SMS alerts
-- Commands:      6 sample WhatsApp commands
-- States covered: MH, DL, TN, KA, TS, UP
-- Languages:      hi, mr, ta, kn, te

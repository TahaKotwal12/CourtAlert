-- =============================================================================
-- CourtAlert Database Schema
-- PostgreSQL 15 (NeonDB)
-- 6 Tables: users, registrations, hearings, notifications,
--            whatsapp_commands, courts
-- =============================================================================

-- ---------------------------------------------------------------------------
-- EXTENSIONS
-- ---------------------------------------------------------------------------

-- gen_random_uuid() is built-in from PostgreSQL 13+, no extension needed.
-- pgcrypto is only needed if you want crypt() for passwords at DB level.

-- ---------------------------------------------------------------------------
-- ENUM TYPES
-- ---------------------------------------------------------------------------

CREATE TYPE user_role         AS ENUM ('admin', 'ngo_user');
CREATE TYPE channel_type      AS ENUM ('whatsapp', 'sms');
CREATE TYPE notification_status AS ENUM ('sent', 'delivered', 'failed', 'retrying');
CREATE TYPE command_type      AS ENUM ('REG', 'STOP', 'STATUS', 'UNKNOWN');

-- ---------------------------------------------------------------------------
-- HELPER: auto-update updated_at column
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TABLE: users
-- NGO and admin accounts
-- =============================================================================

CREATE TABLE users (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    email            VARCHAR(255)  NOT NULL UNIQUE,
    hashed_password  VARCHAR(255)  NOT NULL,
    full_name        VARCHAR(200)  NOT NULL,
    org_name         VARCHAR(200),
    role             user_role     NOT NULL DEFAULT 'ngo_user',
    is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- TABLE: registrations
-- Core table — one row per litigant-case subscription
-- =============================================================================

CREATE TABLE registrations (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    cnr_number       VARCHAR(20)   NOT NULL,
    phone_number     VARCHAR(15)   NOT NULL,
    language         VARCHAR(5)    NOT NULL DEFAULT 'hi',  -- hi/mr/te/ta/kn/en
    case_title       TEXT,
    court_name       VARCHAR(255),
    state_code       VARCHAR(10),
    district_code    VARCHAR(10),
    is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
    last_synced_at   TIMESTAMP,
    registered_by    UUID          REFERENCES users(id) ON DELETE SET NULL,  -- NULL = self-registered via WhatsApp
    created_at       TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_reg_phone  ON registrations (phone_number);
CREATE INDEX idx_reg_cnr    ON registrations (cnr_number);
CREATE INDEX idx_reg_active ON registrations (is_active) WHERE is_active = TRUE;

-- =============================================================================
-- TABLE: hearings
-- Hearing date cache fetched from eCourts API
-- =============================================================================

CREATE TABLE hearings (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_id  UUID          NOT NULL REFERENCES registrations(id) ON DELETE CASCADE,
    hearing_date     DATE          NOT NULL,
    hearing_type     VARCHAR(100),                            -- e.g. Final Arguments, IA Hearing
    court_room       VARCHAR(50),
    judge_name       VARCHAR(200),
    purpose          TEXT,
    is_completed     BOOLEAN       NOT NULL DEFAULT FALSE,
    fetched_at       TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_hear_date ON hearings (hearing_date);       -- CRON: hearings within N days
CREATE INDEX idx_hear_reg  ON hearings (registration_id);   -- JOIN with registrations

-- =============================================================================
-- TABLE: notifications
-- Alert delivery log — one row per message sent
-- =============================================================================

CREATE TABLE notifications (
    id                UUID                 PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_id   UUID                 NOT NULL REFERENCES registrations(id) ON DELETE CASCADE,
    hearing_id        UUID                 NOT NULL REFERENCES hearings(id) ON DELETE CASCADE,
    channel           channel_type         NOT NULL,
    status            notification_status  NOT NULL DEFAULT 'sent',
    message_text      TEXT                 NOT NULL,
    message_language  VARCHAR(5)           NOT NULL,
    days_before       INT                  NOT NULL,          -- 1, 3, or 7
    twilio_sid        VARCHAR(50),
    error_message     TEXT,
    sent_at           TIMESTAMP            NOT NULL DEFAULT NOW(),
    delivered_at      TIMESTAMP
);

-- Indexes
CREATE INDEX        idx_notif_status ON notifications (status);   -- retry query: WHERE status = 'failed'
CREATE UNIQUE INDEX idx_notif_unique ON notifications (registration_id, hearing_id, days_before);  -- prevent duplicate alerts

-- =============================================================================
-- TABLE: whatsapp_commands
-- All inbound WhatsApp and SMS messages received via Twilio webhook
-- =============================================================================

CREATE TABLE whatsapp_commands (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    from_number         VARCHAR(20)   NOT NULL,
    body                TEXT          NOT NULL,
    command_type        command_type,                                         -- NULL until parsed
    cnr_extracted       VARCHAR(20),
    language_extracted  VARCHAR(5),
    registration_id     UUID          REFERENCES registrations(id) ON DELETE SET NULL,  -- NULL if REG failed/pending
    response_sent       TEXT,
    twilio_sid          VARCHAR(50),
    received_at         TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- TABLE: courts
-- Static reference data — court names, addresses, coordinates
-- =============================================================================

CREATE TABLE courts (
    id             UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    state_code     VARCHAR(10)    NOT NULL,
    district_code  VARCHAR(10),
    court_name     VARCHAR(255)   NOT NULL,
    address        TEXT,
    latitude       DECIMAL(9, 6),
    longitude      DECIMAL(9, 6),
    pin_code       VARCHAR(10)
);

-- Index
CREATE INDEX idx_courts_state ON courts (state_code);

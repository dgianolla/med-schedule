--
-- PostgreSQL database dump
--

-- 

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: appointment_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.appointment_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    default_duration_minutes integer DEFAULT 30 NOT NULL,
    description text,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: appointments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.appointments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_name character varying(200) NOT NULL,
    patient_phone character varying(20) NOT NULL,
    patient_email character varying(200),
    professional_id uuid,
    professional_name character varying(200),
    appointment_type_id uuid,
    specialty character varying(100) NOT NULL,
    scheduled_at timestamp with time zone NOT NULL,
    ends_at timestamp with time zone NOT NULL,
    duration_minutes integer NOT NULL,
    status character varying(30) DEFAULT 'scheduled'::character varying NOT NULL,
    source character varying(30) DEFAULT 'lia'::character varying NOT NULL,
    convenio_id uuid,
    convenio_name character varying(100),
    notes text,
    patient_notes text,
    external_id character varying(200),
    cancelled_at timestamp with time zone,
    cancellation_reason character varying(500),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    patient_id uuid,
    medical_notes text
);


--
-- Name: availability_blocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.availability_blocks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    professional_id uuid,
    specialty character varying(100),
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone NOT NULL,
    reason character varying(200),
    recurring character varying(20) DEFAULT 'none'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: convenios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.convenios (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50),
    active boolean DEFAULT true NOT NULL,
    contact character varying(200),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: patients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.patients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(200) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(200),
    document character varying(30),
    birth_date date,
    address character varying(500),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: professionals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.professionals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(200) NOT NULL,
    specialty character varying(100) NOT NULL,
    specialty_slug character varying(100) NOT NULL,
    external_id character varying(100),
    provider character varying(50) DEFAULT 'local'::character varying NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: provider_routes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.provider_routes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    specialty_slug character varying(100) NOT NULL,
    provider character varying(50) NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scheduling_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduling_settings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    weekday_opening time without time zone DEFAULT '08:00:00'::time without time zone NOT NULL,
    weekday_closing time without time zone DEFAULT '17:00:00'::time without time zone NOT NULL,
    saturday_opening time without time zone DEFAULT '08:00:00'::time without time zone NOT NULL,
    saturday_closing time without time zone DEFAULT '12:00:00'::time without time zone NOT NULL,
    sunday_closed boolean DEFAULT true NOT NULL,
    holidays_closed boolean DEFAULT true NOT NULL,
    buffer_minutes integer DEFAULT 0 NOT NULL,
    max_advance_days integer DEFAULT 60 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: appointment_types appointment_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment_types
    ADD CONSTRAINT appointment_types_pkey PRIMARY KEY (id);


--
-- Name: appointment_types appointment_types_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment_types
    ADD CONSTRAINT appointment_types_slug_key UNIQUE (slug);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: availability_blocks availability_blocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.availability_blocks
    ADD CONSTRAINT availability_blocks_pkey PRIMARY KEY (id);


--
-- Name: convenios convenios_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.convenios
    ADD CONSTRAINT convenios_code_key UNIQUE (code);


--
-- Name: convenios convenios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.convenios
    ADD CONSTRAINT convenios_pkey PRIMARY KEY (id);


--
-- Name: patients patients_phone_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_phone_key UNIQUE (phone);


--
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- Name: professionals professionals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professionals
    ADD CONSTRAINT professionals_pkey PRIMARY KEY (id);


--
-- Name: provider_routes provider_routes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.provider_routes
    ADD CONSTRAINT provider_routes_pkey PRIMARY KEY (id);


--
-- Name: provider_routes provider_routes_specialty_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.provider_routes
    ADD CONSTRAINT provider_routes_specialty_slug_key UNIQUE (specialty_slug);


--
-- Name: scheduling_settings scheduling_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_settings
    ADD CONSTRAINT scheduling_settings_pkey PRIMARY KEY (id);


--
-- Name: professionals uq_professional_name_specialty; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.professionals
    ADD CONSTRAINT uq_professional_name_specialty UNIQUE (name, specialty);


--
-- Name: ix_appointments_external_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointments_external_id ON public.appointments USING btree (external_id);


--
-- Name: ix_appointments_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointments_patient_id ON public.appointments USING btree (patient_id);


--
-- Name: ix_appointments_patient_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointments_patient_phone ON public.appointments USING btree (patient_phone);


--
-- Name: ix_appointments_professional_scheduled; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointments_professional_scheduled ON public.appointments USING btree (professional_id, scheduled_at);


--
-- Name: ix_appointments_scheduled_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointments_scheduled_at ON public.appointments USING btree (scheduled_at);


--
-- Name: ix_appointments_status_scheduled_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointments_status_scheduled_at ON public.appointments USING btree (status, scheduled_at);


--
-- Name: ix_availability_professional_start_end; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_availability_professional_start_end ON public.availability_blocks USING btree (professional_id, start_at, end_at);


--
-- Name: ix_patients_document; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_patients_document ON public.patients USING btree (document);


--
-- Name: ix_patients_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_patients_phone ON public.patients USING btree (phone);


--
-- Name: appointments appointments_appointment_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_appointment_type_id_fkey FOREIGN KEY (appointment_type_id) REFERENCES public.appointment_types(id);


--
-- Name: appointments appointments_professional_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_professional_id_fkey FOREIGN KEY (professional_id) REFERENCES public.professionals(id);


--
-- Name: availability_blocks availability_blocks_professional_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.availability_blocks
    ADD CONSTRAINT availability_blocks_professional_id_fkey FOREIGN KEY (professional_id) REFERENCES public.professionals(id);


--
-- Name: appointments fk_appointments_patient_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT fk_appointments_patient_id FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- PostgreSQL database dump complete
--

-- Fim do arquivou


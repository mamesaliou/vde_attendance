-- -- init.sql
-- -- Script d'initialisation de la base de données

-- -- Supprimer l'énumération existante si elle existe
-- DROP TYPE IF EXISTS userrole CASCADE;

-- -- Créer l'énumération pour les rôles avec les bonnes valeurs
-- CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin');

-- -- Créer la table users
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     username VARCHAR(100) UNIQUE NOT NULL,
--     hashed_password VARCHAR(255) NOT NULL,
--     first_name VARCHAR(100) NOT NULL,
--     last_name VARCHAR(100) NOT NULL,
--     role userrole NOT NULL DEFAULT 'student',
--     is_active BOOLEAN DEFAULT true,
--     class_id INTEGER,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP WITH TIME ZONE
-- );

-- -- Créer la table classes
-- CREATE TABLE IF NOT EXISTS classes (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100) UNIQUE NOT NULL,
--     grade VARCHAR(50) NOT NULL,
--     teacher_id INTEGER,
--     teacher_name VARCHAR(100),
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP WITH TIME ZONE,
--     CONSTRAINT fk_teacher FOREIGN KEY (teacher_id) REFERENCES users(id)
-- );

-- -- Créer la table students
-- CREATE TABLE IF NOT EXISTS students (
--     id SERIAL PRIMARY KEY,
--     first_name VARCHAR(100) NOT NULL,
--     last_name VARCHAR(100) NOT NULL,
--     email VARCHAR(255) UNIQUE,
--     class_id INTEGER NOT NULL,
--     user_id INTEGER,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP WITH TIME ZONE,
--     CONSTRAINT fk_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
--     CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
-- );

-- -- Créer la table attendances
-- CREATE TABLE IF NOT EXISTS attendances (
--     id SERIAL PRIMARY KEY,
--     student_id INTEGER NOT NULL,
--     class_id INTEGER NOT NULL,
--     date DATE NOT NULL,
--     present BOOLEAN DEFAULT true,
--     reason TEXT,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP WITH TIME ZONE,
--     CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
--     CONSTRAINT fk_class_attendance FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
--     UNIQUE(student_id, class_id, date)
-- );

-- -- Créer les indexes pour les performances
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
-- CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);
-- CREATE INDEX IF NOT EXISTS idx_attendances_student_id ON attendances(student_id);
-- CREATE INDEX IF NOT EXISTS idx_attendances_class_id ON attendances(class_id);
-- CREATE INDEX IF NOT EXISTS idx_attendances_date ON attendances(date);

-- -- Insérer les données après avoir créé les tables

-- -- Créer un administrateur par défaut
-- INSERT INTO users (email, username, hashed_password, first_name, last_name, role, is_active) 
-- VALUES (
--     'admin@school.com',
--     'admin',
--     -- Mot de passe: Admin123! (à hasher en production)
--     'Admin123!',
--     'Admin',
--     'System',
--     'admin',  -- ✅ Utilise 'admin' (minuscules) pour correspondre à l'enum
--     true
-- ) ON CONFLICT (email) DO NOTHING;

-- -- Créer un enseignant par défaut
-- INSERT INTO users (email, username, hashed_password, first_name, last_name, role, is_active) 
-- VALUES (
--     'teacher@school.com',
--     'teacher',
--     -- Mot de passe: Teacher123!
--     'Teacher123!',
--     'Jean',
--     'Dupont',
--     'teacher',  -- ✅ Utilise 'teacher' (minuscules)
--     true
-- ) ON CONFLICT (email) DO NOTHING;

-- -- Créer une classe par défaut
-- INSERT INTO classes (name, grade, teacher_name)
-- VALUES (
--     'CM1A',
--     'CM1',
--     'Jean Dupont'
-- ) ON CONFLICT (name) DO NOTHING;

-- -- Lier l'enseignant à la classe
-- UPDATE classes SET teacher_id = (
--     SELECT id FROM users WHERE email = 'teacher@school.com'
-- ) WHERE name = 'CM1A';

-- -- Créer un étudiant par défaut
-- INSERT INTO users (email, username, hashed_password, first_name, last_name, role, is_active, class_id) 
-- VALUES (
--     'student@school.com',
--     'student1',
--     -- Mot de passe: Student123!
--     'Student123!',
--     'Marie',
--     'Martin',
--     'student',  -- ✅ Utilise 'student' (minuscules)
--     true,
--     1  -- Référence à la classe créée ci-dessus
-- ) ON CONFLICT (email) DO NOTHING;

-- -- Créer un enregistrement d'élève pour l'étudiant
-- INSERT INTO students (first_name, last_name, email, class_id, user_id)
-- VALUES (
--     'Marie',
--     'Martin',
--     'student@school.com',
--     1,
--     (SELECT id FROM users WHERE email = 'student@school.com')
-- ) ON CONFLICT (email) DO NOTHING;

-- -- Créer quelques présences de test
-- INSERT INTO attendances (student_id, class_id, date, present, reason)
-- VALUES 
--     ((SELECT id FROM students WHERE email = 'student@school.com'), 1, CURRENT_DATE - INTERVAL '2 days', true, NULL),
--     ((SELECT id FROM students WHERE email = 'student@school.com'), 1, CURRENT_DATE - INTERVAL '1 day', false, 'Maladie'),
--     ((SELECT id FROM students WHERE email = 'student@school.com'), 1, CURRENT_DATE, true, NULL)
-- ON CONFLICT (student_id, class_id, date) DO NOTHING;
-- init.sql
-- Script d'initialisation de la base de données

-- Créer un administrateur par défaut
INSERT INTO users (email, username, hashed_password, first_name, last_name, role, is_active, created_at) 
VALUES (
    'admin@school.com',
    'admin',
    -- Mot de passe: Admin123! (à hasher en production)
    -- Pour la démo, on utilise une version simple
    'Admin123!',
    'Admin',
    'System',
    'admin',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Créer un enseignant par défaut
INSERT INTO users (email, username, hashed_password, first_name, last_name, role, is_active, created_at) 
VALUES (
    'teacher@school.com',
    'teacher',
    -- Mot de passe: Teacher123!
    'Teacher123!',
    'Jean',
    'Dupont',
    'teacher',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Créer une classe par défaut
INSERT INTO classes (name, grade, teacher_name, created_at)
VALUES (
    'CM1A',
    'CM1',
    'Jean Dupont',
    NOW()
) ON CONFLICT (name) DO NOTHING;

-- Créer un étudiant par défaut
INSERT INTO users (email, username, hashed_password, first_name, last_name, role, is_active, class_id, created_at) 
VALUES (
    'student@school.com',
    'student1',
    -- Mot de passe: Student123!
    'Student123!',
    'Marie',
    'Martin',
    'student',
    true,
    1,  -- Référence à la classe créée ci-dessus
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Lier l'enseignant à la classe
UPDATE classes SET teacher_id = (
    SELECT id FROM users WHERE email = 'teacher@school.com'
) WHERE name = 'CM1A';

-- Créer un enregistrement d'élève pour l'étudiant
INSERT INTO students (first_name, last_name, email, class_id, user_id, created_at)
VALUES (
    'Marie',
    'Martin',
    'student@school.com',
    1,
    (SELECT id FROM users WHERE email = 'student@school.com'),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Créer quelques présences de test
INSERT INTO attendances (student_id, class_id, date, present, reason, created_at)
VALUES 
    ((SELECT id FROM students WHERE email = 'student@school.com'), 1, CURRENT_DATE - INTERVAL '2 days', true, NULL, NOW()),
    ((SELECT id FROM students WHERE email = 'student@school.com'), 1, CURRENT_DATE - INTERVAL '1 day', false, 'Maladie', NOW()),
    ((SELECT id FROM students WHERE email = 'student@school.com'), 1, CURRENT_DATE, true, NULL, NOW())
ON CONFLICT (student_id, class_id, date) DO NOTHING;
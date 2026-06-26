USE cinema;

SELECT 
    s.id_session,
    m.name AS film,
    h.number AS hall,
    s.date,
    s.time,
    s.price
FROM sessions s
JOIN movies m ON s.id_film = m.id_film
JOIN halls h ON s.id_hall = h.id_hall
WHERE s.date = CURDATE();
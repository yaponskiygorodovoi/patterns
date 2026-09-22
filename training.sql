WITH stays as (
  SELECT 
      visit_id,
      room_id,
      MAX(CASE WHEN type = 'CHECKIN' THEN dt END) as checin_dt,
      MAX(CASE WHEN type = 'CHECKOUT' THEN dt END) as ckeckout_dt
  FROM visits
  GROUP BY visit_id,room_id     
)
 
rev_by_room as (
SELECT 
  DATE_TRUNC('mont', s.checkin_dt) as mounth,
  s.room_id,
  SUM((s.ckeckout_dt - checkin_dt)* r.price) as revenue
FROM stays s 
JOIN rooms r 
    ON s.room_id = r.room_id 
GROUP BY 
     DATE_TRUNC('mont', s.checkin_dt),
     s.room_id 
               
)
ranked as (
  SELECT 
      month,
      room_id,
      revenue,
      RANK() OVER(PARTITION BY month ORDER BY revenue DESC) as rnk 
  FROM rev_by_room    
)

SELECT 
     month,
     room.
     revenue 
FROM ranked 
WHERE rnk <= 3;      
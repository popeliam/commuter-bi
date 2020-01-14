with routes as (
select trip_id, array_agg(street) route from (
	select 
		ts.trip_id
		, row_number() over (partition by ts.trip_id order by ts.distance_meters desc) dist_rank
		, step_order
		, case when position('right' in ts.description) > 0 then substring(ts.description,position('right' in ts.description)+6,length(ts.description))
			when position('left' in ts.description) > 0 then substring(ts.description,position('left' in ts.description)+5,length(ts.description))
			else ts.description end street
	from trip_steps ts
	order by trip_id, step_order asc
) q 
where dist_rank < 4
group by trip_id
) select c.commute_name
, case when substring(c.commute_name,1,4) = 'Work' then 'To Home' else 'To Work' end commute_type
, c.commute_id
, r.route
, t.weather
, t.departure_ts
, t.duration_seconds
, t.distance_meters
from commutes c
left join trips t on t.commute_id = c.commute_id
left join routes r on r.trip_id = t.trip_id
where c.is_active
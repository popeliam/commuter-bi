select
text(l.location_id)||'_'||text(l2.location_id) commute_id
, l.location_name ||' to ' ||l2.location_name commute_name
, case when l.commute_active and l2.commute_active then true else false end active
, text(l.latitude) || ',' || text(l.longitude) from_lat_long
, text(l2.latitude) || ',' || text(l2.longitude) to_lat_long
from locations l
left join locations l2 on l2.location_id <> l.location_id
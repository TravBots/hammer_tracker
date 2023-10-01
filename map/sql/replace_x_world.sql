drop table if exists x_world; 

create table if not exists x_world (
    id int,
    x_coordinate int,
    y_coordinate int,
    tribe_id int,
    village_id int,
    village_name varchar,
    player_id int,
    player_name varchar,
    alliance_id int,
    alliance_tag varchar,
    population int,
    region int,
    capital boolean,
    city int,
    harbor int,
    victory_points int
);
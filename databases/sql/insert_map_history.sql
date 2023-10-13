create table if not exists map_history (
    id varchar primary key not null,
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
    capital boolean,
    inserted_at timestamp
);

insert into map_history 
    select
        cast(x_coordinate as str)||'|'||cast(y_coordinate as str)||'@'||cast(unixepoch() as str) as id,
        x_coordinate,
        y_coordinate,
        tribe_id,
        village_id,
        village_name,
        player_id,
        player_name,
        alliance_id,
        alliance_tag,
        population,
        capital,
        unixepoch() as inserted_at 
    from x_world;

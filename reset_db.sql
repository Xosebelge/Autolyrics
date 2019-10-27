
drop table if exists words;

drop table if exists songs;

create table if not exists songs (
	song_id serial not null primary key,
	artist text not null,
	title text not null,
	filename_full text not null,
	filename_minus text,
	filename_voice text
);

create table if not exists words (
	word_id serial not null primary key,
	song_id integer not null references songs(song_id) on delete cascade,
	word text not null,
	word_index integer not null,
	time_start real not null,
	time_end real not null
);


-- basic inserts to start with the "dummy" instructors/devices etc
start transaction;

insert into device (userAgent, imei)
values
    ('Mobile Browser Mozilla etc.', 'NOTAVALIDPHONEID');
insert into instructor (name, email, phone, address)
values
    ('Jane Doe', 'dummy@jk.is', '1-800-DONT-CALL', 'Australia');
insert into speaker (name, deviceImei)
values
    ('John Doe', 'NOTAVALIDPHONEID');
insert into speaker_info (speakerId, s_key, s_value)
values
    (1, 'sex', 'male'),
    (1, 'dob', '1991-1995'),
    (1, 'height', '170');
insert into session (speakerId, instructorId, deviceId, location, start, end, comments)
values 
    (1, 1, 1, 'Norway etc.', '2015/10/1 15:00:00.00', '2015/10/1 15:00:30.05', 'Much wind.');

commit;

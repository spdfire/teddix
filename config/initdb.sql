
DROP DATABASE teddix;
CREATE DATABASE teddix;

USE teddix; 


CREATE TABLE server ( 
	id INT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50), 
	created DATETIME, 

	PRIMARY KEY ( id )
);

-- container for cfg2html & ora2html
CREATE TABLE extra ( 
	id INT NOT NULL AUTO_INCREMENT, 
	server_id INT NOT NULL, 
	created DATETIME NOT NULL, 
	cfg2html MEDIUMTEXT, 
	ora2html MEDIUMTEXT, 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id) 
);

-- Baseline 
CREATE TABLE baseline ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	hostname VARCHAR(50), 
	program VARCHAR(50), 
	scantime VARCHAR(25), 
	version VARCHAR(25), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id)
);

-- Hardware Informations 
CREATE TABLE sysboard ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	boardtype VARCHAR(25), 
	serialnumber VARCHAR(50), 
	manufacturer VARCHAR(50), 
	productname VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id)
);

CREATE TABLE processor ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	cores VARCHAR(25), 
	extclock VARCHAR(25), 
	familly VARCHAR(25), 
	htsystem VARCHAR(10), 
	procid VARCHAR(25), 
	partnumber VARCHAR(50), 
	serialnumber VARCHAR(50), 
	clock VARCHAR(25), 
	threads VARCHAR(25), 
	proctype VARCHAR(50), 
	procversion VARCHAR(50),

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id)
);

CREATE TABLE memorymodule ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	bank VARCHAR(25), 
	formfactor VARCHAR(25), 
	location VARCHAR(50), 
	manufacturer VARCHAR(50), 
	memorytype VARCHAR(25), 
	partnumber VARCHAR(50), 
	serialnumber VARCHAR(50), 
	modulesize VARCHAR(25), 
	width VARCHAR(25), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id)
);

CREATE TABLE bios ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	releasedate VARCHAR(25), 
	vendor VARCHAR(25), 
	version VARCHAR(25), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id)
);


-- OS Informations 
CREATE TABLE system ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	arch VARCHAR(25), 
	detail VARCHAR(50), 
	kernel VARCHAR(50), 
	manufacturer VARCHAR(50), 
	name VARCHAR(50), 
	serialnumber VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id)
);

CREATE TABLE package ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	description VARCHAR(250), 
	files VARCHAR(50), 
	homepage VARCHAR(250), 
	name VARCHAR(50), 
	pkgsize VARCHAR(50), 
	section VARCHAR(50), 
	signed VARCHAR(50), 
	installedsize VARCHAR(50), 
	status VARCHAR(50), 
	version VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

CREATE TABLE filesystem ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	device VARCHAR(50), 
	fstype VARCHAR(50), 
	fsfree VARCHAR(50), 
	name VARCHAR(50), 
	fssize VARCHAR(50), 
	fsused VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

CREATE TABLE swap ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	device VARCHAR(50), 
	swapfree VARCHAR(50), 
	swapsize VARCHAR(50), 
	swaptype VARCHAR(50), 
	swapused VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

-- Network configuration 
CREATE TABLE nic ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	MTU VARCHAR(25), 
	RXbytes VARCHAR(25), 
	RXpackets VARCHAR(25), 
	TXbytes VARCHAR(25), 
	TXpackets VARCHAR(25), 
	description VARCHAR(50), 
	macaddress VARCHAR(50), 
	name VARCHAR(50), 
	nictype VARCHAR(50), 
	status VARCHAR(50), 
	driver VARCHAR(50), 
	kernmodule VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

CREATE TABLE ipv4 ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	nic_id INT NOT NULL,
	address VARCHAR(25), 
	broadcast VARCHAR(25), 
	mask VARCHAR(25), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id),
	FOREIGN KEY (nic_id) REFERENCES nic(id)
);

CREATE TABLE ipv6 ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	nic_id INT NOT NULL,
	address VARCHAR(50), 
	broadcast VARCHAR(50), 
	mask VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id),
	FOREIGN KEY (nic_id) REFERENCES nic(id)
);


CREATE TABLE domain ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

CREATE TABLE dnssearch ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);


CREATE TABLE nameserver ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	address VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

CREATE TABLE route4 ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	destination VARCHAR(50), 
	flags VARCHAR(10), 
	gateway VARCHAR(50), 
	interface VARCHAR(50), 
	mask VARCHAR(50), 
	metric VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);


CREATE TABLE route6 ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	destination VARCHAR(50), 
	flags VARCHAR(10), 
	gateway VARCHAR(50), 
	interface VARCHAR(50), 
	mask VARCHAR(50), 
	metric VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

-- System accounts
CREATE TABLE sysgroup ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);


CREATE TABLE sysuser ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	expire VARCHAR(50), 
	destination VARCHAR(50), 
	gid  VARCHAR(50),
	groups VARCHAR(250), 
	hashtype VARCHAR(25), 
	home VARCHAR(50), 
	locked VARCHAR(25), 
	login VARCHAR(50), 
	shell VARCHAR(50), 
	uid INT,

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);


-- Language settings
CREATE TABLE regional ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	timezone VARCHAR(50), 
	charset VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

-- Process list 
CREATE TABLE process ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	command VARCHAR(250), 
	cputime  VARCHAR(50), 
	owner VARCHAR(50), 
	pcpu  VARCHAR(50), 
	pid  VARCHAR(50), 
	pmemory  VARCHAR(50), 
	priority  VARCHAR(50), 
	sharedsize  VARCHAR(50), 
	virtsize  VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);

-- Service list 
CREATE TABLE service ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	autostart VARCHAR(50), 
	name VARCHAR(50), 
	running VARCHAR(50), 

	PRIMARY KEY (id),
	FOREIGN KEY (server_id) REFERENCES server(id),
	FOREIGN KEY (baseline_id) REFERENCES baseline(id),
	FOREIGN KEY (system_id) REFERENCES system(id)
);




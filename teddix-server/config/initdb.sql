
DROP DATABASE teddix;
CREATE DATABASE teddix;

USE teddix; 


CREATE TABLE server ( 
	id INT NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50), 
	created DATETIME, 

	PRIMARY KEY (id)
) ENGINE=InnoDB;

-- container for cfg2html
CREATE TABLE extra ( 
	id INT NOT NULL AUTO_INCREMENT, 
	server_id INT NOT NULL, 
	created DATETIME NOT NULL, 
	cfg2html MEDIUMTEXT, 
	bootlog MEDIUMTEXT, 
	dmesg MEDIUMTEXT, 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_extra FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE 
) ENGINE=InnoDB;

-- Baseline 
CREATE TABLE baseline ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	created DATETIME NOT NULL, 
	hostname VARCHAR(50), 
	program VARCHAR(50), 
	scantime VARCHAR(25), 
	version VARCHAR(25), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_baseline FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Hardware Informations 
CREATE TABLE chassis( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	manufacturer VARCHAR(50), 
	serialnumber VARCHAR(50), 
	thermalstate VARCHAR(50), 
	chassistype VARCHAR(50), 
	version VARCHAR(25), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_chassis FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_chassis FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE baseboard ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	manufacturer VARCHAR(50), 
	productname VARCHAR(50), 
	serialnumber VARCHAR(50), 
	version VARCHAR(25), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_baseboard FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_baseboard FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

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
	speed VARCHAR(25), 
	socket VARCHAR(25), 
	threads VARCHAR(25), 
	proctype VARCHAR(50), 
	procversion VARCHAR(50),

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_processor FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_processor FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE memorymodule ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	bank VARCHAR(25), 
	formfactor VARCHAR(25), 
	location VARCHAR(50), 
	manufacturer VARCHAR(50), 
	modulesize VARCHAR(25), 
	memorytype VARCHAR(25), 
	partnumber VARCHAR(50), 
	serialnumber VARCHAR(50), 
	speed VARCHAR(25), 
	width VARCHAR(25), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_memorymodule FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_memorymodule FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE blockdevice( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	name VARCHAR(25), 
	devtype VARCHAR(25), 
	vendor VARCHAR(25), 
	model VARCHAR(25), 
	sectors VARCHAR(25), 
	sectorsize VARCHAR(10), 
	rotational VARCHAR(5), 
	readonly VARCHAR(5), 
	removable VARCHAR(5), 
	major VARCHAR(5), 
	minor VARCHAR(5), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_blockdevice FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_blockdevice FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE pcidevice( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	path VARCHAR(25), 
	devtype VARCHAR(50), 
	vendor VARCHAR(50), 
	model VARCHAR(50), 
	revision VARCHAR(25), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_pcidevice FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_pcidevice FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;



CREATE TABLE bios ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	releasedate VARCHAR(25), 
	revision VARCHAR(25), 
	vendor VARCHAR(25), 
	version VARCHAR(25), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_bios FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE ,
	CONSTRAINT fk_baselineid_bios FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


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
	CONSTRAINT fk_serverid_system FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_system FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE package ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	arch VARCHAR(50), 
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
	CONSTRAINT fk_serverid_package FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_package FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_package FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE patch ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 
	description VARCHAR(250), 
	patchtype VARCHAR(50), 
	version VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_patch FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_patch FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_patch FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE filesystem ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	fsdevice VARCHAR(50), 
	fsname VARCHAR(50), 
	fstype VARCHAR(50), 
	fsopts VARCHAR(50), 
	fstotal VARCHAR(50), 
	fsused VARCHAR(50), 
	fsfree VARCHAR(50), 
	fspercent VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_filesystem FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_filesystem FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_filesystem FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

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
	CONSTRAINT fk_serverid_swap FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_swap FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_swap FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Network configuration 
CREATE TABLE nic ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 
	description VARCHAR(50), 
	nictype VARCHAR(50), 
	status VARCHAR(50), 
	RXpackets VARCHAR(25), 
	TXpackets VARCHAR(25), 
	RXbytes VARCHAR(25), 
	TXbytes VARCHAR(25), 
	driver VARCHAR(50), 
	drvver VARCHAR(50), 
	firmware VARCHAR(50), 
	macaddress VARCHAR(50), 
	kernmodule VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_nic FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_nic FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_nic FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

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
	CONSTRAINT fk_serverid_ipv4 FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_ipv4 FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_ipv4 FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_nicid_ipv4 FOREIGN KEY (nic_id) REFERENCES nic(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

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
	CONSTRAINT fk_serverid_ipv6 FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_ipv6 FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_ipv6 FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_nicid_ipv6 FOREIGN KEY (nic_id) REFERENCES nic(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE domain ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_domain FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_domain FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_domain FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE dnssearch ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_dnssearch FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_dnssearch FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_dnssearch FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE nameserver ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	address VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_nameserver FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_nameserver FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_nameserver FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

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
	CONSTRAINT fk_serverid_route4 FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_route4 FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_route4 FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


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
	CONSTRAINT fk_serverid_route6 FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE ,
	CONSTRAINT fk_baselineid_route6 FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_route6 FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- System accounts
CREATE TABLE sysgroup ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	name VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_sysgroup FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_sysgroup FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_sysgroup FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE sysuser ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	login VARCHAR(50), 
	uid VARCHAR(50),
	gid  VARCHAR(50),
	comment VARCHAR(50), 
	home VARCHAR(50), 
	shell VARCHAR(50), 
	locked VARCHAR(25), 
	hashtype VARCHAR(25), 
	groups VARCHAR(250), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_sysuser FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_sysuser FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_sysuser FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- Language settings
CREATE TABLE regional ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	timezone VARCHAR(50), 
	charset VARCHAR(50), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_regional FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE ,
	CONSTRAINT fk_baselineid_regional FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_regional FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Process list 
CREATE TABLE process ( 
	id INT NOT NULL AUTO_INCREMENT,
	server_id INT NOT NULL,
	baseline_id INT NOT NULL,
	system_id INT NOT NULL,
	pid  VARCHAR(50), 
	owner VARCHAR(50), 
	cpusystime  VARCHAR(50), 
	cpuusertime  VARCHAR(50), 
	pcpu  VARCHAR(50), 
	pmemory  VARCHAR(50), 
	priority  VARCHAR(50), 
	status  VARCHAR(50), 
	name  VARCHAR(50), 
	command VARCHAR(250), 

	PRIMARY KEY (id),
	CONSTRAINT fk_serverid_process FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_process FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_process FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

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
	CONSTRAINT fk_serverid_service FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_baselineid_service FOREIGN KEY (baseline_id) REFERENCES baseline(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_systemid_service FOREIGN KEY (system_id) REFERENCES system(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;




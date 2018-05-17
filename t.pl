#!/usr/bin/perl
use DBI;
$logfile = '/home/vpcloud/procmail.log';
$what = '';
$header = 1;
my $driver = "mysql"; 
my $database = "vrealize";
my $dsn = "DBI:$driver:database=$database";
my $userid = "root";
my $password = "jordan";

my $dbh = DBI->connect($dsn, $userid, $password ) or die $DBI::errstr;
my $hostname = "vmdboraclea-01.vpc.dev.scl1.us.tribalfusion.net";
my $sth = $dbh->prepare("SELECT id from vrealize where name='$hostname'");
$sth->execute() or die $DBI::errstr;
print "Number of rows found :" + $sth->rows;
while (my @row = $sth->fetchrow_array()) {
my ($id ) = @row;
   print "$id";
}

#!/usr/bin/perl
use strict;
use warnings;
my $str = "+15d";
my @fields = split /d/, $str;
my $howmany = $fields[0];
print "$howmany\n";

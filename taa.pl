#!/usr/bin/perl
sub  trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return lc "$s" };
$a = '+FOO BAR';
$b = trim("$a");
 
print "$b";

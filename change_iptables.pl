#!/usr/bin/perl
use strict;
use Getopt::Long;
use IPTables::ChainMgr;

my $ipt_bin = '/sbin/iptables'; # can set this to /sbin/ip6tables

my %opts = (
    'iptables' => $ipt_bin,
    'iptout'   => '/tmp/iptables.out',
    'ipterr'   => '/tmp/iptables.err',
    'debug'    => 0,
    'verbose'  => 0,

    ### advanced options
    'ipt_alarm' => 5,  ### max seconds to wait for iptables execution.
    'ipt_exec_style' => 'waitpid',  ### can be 'waitpid',
                                    ### 'system', or 'popen'.
    'ipt_exec_sleep' => 1, ### add in time delay between execution of
                           ### iptables commands (default is 0).
);

my $ipt_obj = new IPTables::ChainMgr(%opts)
    or die "[*] Could not acquire IPTables::ChainMgr object";


my ( $test, $ipaddress, $rulenum, $chain_rules, $del, $add);
GetOptions(
					'test|t'    => \$test,
					'd|t'    => \$del,
					'a|t'    => \$add,
	        'ip=s'  => \$ipaddress,
);

if($test){
		print "Debug mode.\n";
		if($ipaddress){
				print "$ipaddress\n";
		}
}

if(($ipaddress) && not ($test)){
	print "Find and Delete or Add $ipaddress\n";

 	my $rv = 0;
 	my $out_ar = "";
 	my $errs_ar = "";
 	
 	($rulenum, $chain_rules) = $ipt_obj->find_ip_rule("$ipaddress",
 	      '0.0.0.0/0', 'filter', 'INPUT', 'ACCEPT',
 	      {'normalize' => 1});
 	if ($rulenum) {
 	    print "matched rule $rulenum out of $chain_rules rules\n";
			print "Existing\n"
 	}
	else{
		 print "Not Found.\n"
	}
 	
	if(($add) && not ($rulenum)){
		  print "Add ...\n";
			($rv, $out_ar, $errs_ar) = $ipt_obj->add_ip_rule($ipaddress,
				'0.0.0.0/0', 1, 'filter', 'INPUT', 'ACCEPT',
			  {'normalize' => 1});
			$rulenum = 0;
  }		
  if(($del) && ($rulenum)){	
		  print "Del ...\n";
			($rv, $out_ar, $errs_ar) = $ipt_obj->delete_ip_rule($ipaddress,
			  '0.0.0.0/0', 'filter', 'INPUT', 'ACCEPT',
				{'normalize' => 1});
	}
	if($rv){	
			print "Success\n";
		}
	else{		
			if($out_ar){print "$out_ar\n"};	
			if($errs_ar){print "$errs_ar\n"};	
		}

}

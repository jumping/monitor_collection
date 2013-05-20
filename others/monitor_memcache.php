<?php
$VERSION='$Id: monitor-memcache.php,v 1.0 2010/03/19 21:11:11 Jumping $';

define('DATE_FORMAT','Y/m/d H:i:s');
define('MAX_ITEM_DUMP',50);
define('mem_size_alert',452653184);
define('curr_items_alert',358250);

$MEMCACHE_SERVERS = array('10.252.147.239:11211','10.194.95.214:11211','10.194.95.196:11211'); // add more as an array
//$MEMCACHE_SERVERS = array('192.168.1.3:11211','192.168.1.2:11211'); // add more as an array


function sendMemcacheCommands($command){
    global $MEMCACHE_SERVERS;
	$result = array();

	foreach($MEMCACHE_SERVERS as $server){
		$strs = explode(':',$server);
		$host = $strs[0];
		$port = $strs[1];
		$result[$server] = sendMemcacheCommand($host,$port,$command);
	}
	return $result;
}
function sendMemcacheCommand($server,$port,$command){

	$s = @fsockopen($server,$port);
	if (!$s){
		die("Cant connect to:".$server.':'.$port);
	}

	fwrite($s, $command."\r\n");

	$buf='';
	while ((!feof($s))) {
		$buf .= fgets($s, 256);
		if (strpos($buf,"END\r\n")!==false){ // stat says end
		    break;
		}
		if (strpos($buf,"DELETED\r\n")!==false || strpos($buf,"NOT_FOUND\r\n")!==false){ // delete says these
		    break;
		}
		if (strpos($buf,"OK\r\n")!==false){ // flush_all says ok
		    break;
		}
	}
    fclose($s);
    return parseMemcacheResults($buf);
}
function parseMemcacheResults($str){
    
	$res = array();
	$lines = explode("\r\n",$str);
	$cnt = count($lines);
	for($i=0; $i< $cnt; $i++){
	    $line = $lines[$i];
		$l = explode(' ',$line,3);
		if (count($l)==3){
			$res[$l[0]][$l[1]]=$l[2];
			if ($l[0]=='VALUE'){ // next line is the value
			    $res[$l[0]][$l[1]] = array();
			    list ($flag,$size)=explode(' ',$l[2]);
			    $res[$l[0]][$l[1]]['stat']=array('flag'=>$flag,'size'=>$size);
			    $res[$l[0]][$l[1]]['value']=$lines[++$i];
			}
		}elseif($line=='DELETED' || $line=='NOT_FOUND' || $line=='OK'){
		    return $line;
		}
	}
	return $res;

}

function dumpCacheSlab($server,$slabId,$limit){
    list($host,$port) = explode(':',$server);
    $resp = sendMemcacheCommand($host,$port,'stats cachedump '.$slabId.' '.$limit);

   return $resp;

}

function getCacheItems(){
 $items = sendMemcacheCommands('stats items');
 $serverItems = array();
 $totalItems = array();
 foreach ($items as $server=>$itemlist){
    $serverItems[$server] = array();
    $totalItems[$server]=0;
    if (!isset($itemlist['STAT'])){
        continue;
    }

    $iteminfo = $itemlist['STAT'];

    foreach($iteminfo as $keyinfo=>$value){
        if (preg_match('/items\:(\d+?)\:(.+?)$/',$keyinfo,$matches)){
            $serverItems[$server][$matches[1]][$matches[2]] = $value;
            if ($matches[2]=='number'){
                $totalItems[$server] +=$value;
            }
        }
    }
 }
 return array('items'=>$serverItems,'counts'=>$totalItems);
}
function getMemcacheStats($total=true){
	$resp = sendMemcacheCommands('stats');
	if ($total){
		$res = array();
		foreach($resp as $server=>$r){
			foreach($r['STAT'] as $key=>$row){
				if (!isset($res[$key])){
					$res[$key]=null;
				}
				switch ($key){
					case 'pid':
						$res['pid'][$server]=$row;
						break;
					case 'uptime':
						$res['uptime'][$server]=$row;
						break;
					case 'time':
						$res['time'][$server]=$row;
						break;
					case 'version':
						$res['version'][$server]=$row;
						break;
					case 'pointer_size':
						$res['pointer_size'][$server]=$row;
						break;
					case 'rusage_user':
						$res['rusage_user'][$server]=$row;
						break;
					case 'rusage_system':
						$res['rusage_system'][$server]=$row;
						break;
					case 'curr_items':
						$res['curr_items']+=$row;
						break;
					case 'total_items':
						$res['total_items']+=$row;
						break;
					case 'bytes':
						$res['bytes']+=$row;
						break;
					case 'curr_connections':
						$res['curr_connections']+=$row;
						break;
					case 'total_connections':
						$res['total_connections']+=$row;
						break;
					case 'connection_structures':
						$res['connection_structures']+=$row;
						break;
					case 'cmd_get':
						$res['cmd_get']+=$row;
						break;
					case 'cmd_set':
						$res['cmd_set']+=$row;
						break;
					case 'get_hits':
						$res['get_hits']+=$row;
						break;
					case 'get_misses':
						$res['get_misses']+=$row;
						break;
					case 'evictions':
						$res['evictions']+=$row;
						break;
					case 'bytes_read':
						$res['bytes_read']+=$row;
						break;
					case 'bytes_written':
						$res['bytes_written']+=$row;
						break;
					case 'limit_maxbytes':
						$res['limit_maxbytes']+=$row;
						break;
					case 'threads':
						$res['rusage_system'][$server]=$row;
						break;
				}
			}
		}
		return $res;
	}
	return $resp;
}



function bsize($s) {
	foreach (array('','K','M','G') as $i => $k) {
		if ($s < 1024) break;
		$s/=1024;
	}
	return sprintf("%5.1f %sBytes",$s,$k);
}

function sendMail($alertMsg){
  $to="15618501108@186sh.com";
  $subject="Memcache Alert";
  $body=$alertMsg;
  $result=mail($to,$subject,$body);
  if($result){
    echo "Send mail. Success!";
  }

}

$memcacheStats = getMemcacheStats();
$memcacheStatsSingle = getMemcacheStats(false);

$mem_size = $memcacheStats['limit_maxbytes'];
echo "mem size : ".bsize($mem_size)."\n";
if ($mem_size < $mem_size_alert){
  echo "alert"."\n";
  sendMail("Memory Size Drop");
}

$mem_used = $memcacheStats['bytes'];
echo "mem used : ".bsize($mem_used)."\n";

$mem_avail= $mem_size-$mem_used;
echo "mem avail : ".bsize($mem_avail)."\n";

//$startTime = time()-array_sum($memcacheStats['uptime']);
//echo "start Time : ".$startTime."\n";

$curr_items = $memcacheStats['curr_items'];
echo "curr items : ".$curr_items."\n";
if ($curr_items < $curr_items_alert){
  echo "alert"."\n";
  sendMail("Memory Items DROP!");
}

//$total_items = $memcacheStats['total_items'];
//echo "total items : ".$total_items."\n";


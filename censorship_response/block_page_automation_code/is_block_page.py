def is_block_page(header, body):
    if(header is None):
        print("HEADER IS NONE DUMMY")
    if (body is None):
        print("BODY IS NONE")
    comments = {}
    comments['reason'] = []
    blockpage_body_fingerprints = {
    'IR1': u'iframe src=\"http://10.10',
    'IR2': u'window.open(\"http://peyvandha.ir',

    'TR1': u'<title>Telekomünikasyon İletişim Başkanlığı</title>',
    'TR2': u'uyarınca yapılan teknik inceleme ve hukuki değerlendirme sonucunda bu internet',
    'TR3': u'http://www.btk.gov.tr</a>&nbsp;|\n\t   <a class=\"link\" target = \"_blank\" href=\"http://www.guvenlinet.org\">http://www.guvenlinet.org</a>&nbsp;|\n\t   <a class=\"link\" target = \"_blank\" href=\"http://www.ihbarweb.org.tr\">http://www.ihbarweb.org.tr</a>', # new in 2017-12
    'TR4': u'The protection measure has been taken for this website',
    'TR5': u'After technical analysis and legal consideration based on the', # this should be deleted, a certain website contains this text in its news
    'TR6': u'This site has been blocked in response to a unilateral order from a Turkish authority',

    'GR': u'www.gamingcommission.gov.gr/index.php/forbidden-access-black-list/',

    'RU1': u'http://eais.rkn.gov.ru/',
    'RU2': u'Access to the requested resource has been blocked<br/>by the decision of public authorities.',
    'RU3': u'The page is blocked due to the decision of the authorities in your area.', #error451

    'BE': u'that is considered illegal according to Belgian legislation',

    'IT': u'GdF Stop Page',

    'CY': u'nba.com.cy/Eas/eas.nsf/All/6F7F17A7790A55C8C2257B130055C86F',

    'DK': u'lagt at blokere for adgang til siden.',

    'FR': u'xtpage = "page-blocage-terrorisme"',

    'MY': u'Makluman/Notification',

    'RO': u'Accesul dumneavoastră către acest site a fost restricționat',

    'GF': u'xtpage = "page-blocage-terrorisme"',

    'KR1': u'http://warning.or.kr',
    'KR2': u'http://www.warning.or.kr', # new in 2017-03
    'KR3': u'meta name=\"kcsc\" content=\"blocking', #new in 2017-03
    'IN1': u'The page you have requested has been blocked',
    'IN2': u'The URL has been blocked as per the instructions of the Competent Government Authority/ in compliance to the orders of Court of Law.', #NEW in 2017-08
    'IN3': u'Your requested URL has been blocked as per the directions received from Department of Telecommunications', #NEW
    'IN4': u'is website/URL has been blocked as per instructions from Department of Telecommunications of India', #new
    'IN5': u'<iframe src=\"http://www.airtel.in/dot/?dpid=1&dpruleid=3', #NEW
    'IN6': u'<iframe src=\"http://www.airtel.in/dot/?', #NEW

    # hellais blockpages
    'UK' : u'Sorry, the web page you have requested is not available through Virgin Media.',
    'BE1' : u'that is considered illegal according to Belgian legislation.',
    'BU' : u'The access to requested URL has been denied.',
    'EG' : u'attack site and has been blocked to protect your computer',

    # citizenlab blockpages
    'TH1' : u'<td><img src=\"blockwebx.png\"',
    'TH2' : u'</strong>The page you are trying to visit has been blocked by the Ministry of Information and Communication Technology.</p>',
    'TH3' : u'<p class="textred">The Ministry of Information and Communication Technology has temporarily ceased the service to access such kind of information.</p>',
    'TH4' : u'<center> <img src = \"ict.jpg\"> </center>',
    'TH5' : u'<center> <img src = \"ict2.jpg\"> </center>',
    'TH6' : u'<center> <img src = \"graffic.png\"> </center>',
    'TH7' : u'<img src=\"images/nbtc-20140525.png\">',
    'TH8' : u'<span class=\"textred\">An  access to such information has been temporarily ceased </span><br',
    'TH9' : u'it could have an affect on or be against the security of the Kingdom, public order or good morals.</font><br>',
    'TH10' : u'This URL has been blocked due to Court\'s order or MICT request.',

    'AE'  : u'<title>Surf Safely | This website is not accessible in the UAE.</title>',
    'ID1' : u'13px;\">We are blocking this abusive site as stated by the Indonesia regulation in order to provide Internet Sehat.</em>',
    'ID2' : u'<img src=\"/images/internetsehat_fm.jpg\"',
    'ID3' : u'src=\"InternetSehat.jpg\" alt=\"netSAFE\">',
    'ID4' : u'<img src=\"logo_netsafe.JPG\" alt=\"netSAFE\">',
    'ID5' : u'<b>Situs ini </b> tidak bisa diakses melalui jaringan ini sesuai peraturan perundang-undangan.</div>',
    'ID6' : u'meta name=\"keywords\" content=\"telkom indonesia, internet sehat, positif, internet positif\" />',
    'ID7' : u'<p><img src=\"../deny/images/icon.jpg\"',
    'ID8' : u'id=inner_text>Pelanggan terhormat, sesuai dengan peraturan perundangan situs tujuan anda tidak dapat diakses. Mohon maaf untuk ketidaknyamanannya, silahkan mencoba kembali.',

    'IN7' : u'This website/URL has been blocked until further notice either pursuant to Court orders or on the Directions issued by the Department of Telecommunications',
    'IN7b' : u'This website/url has been blocked until further notice either pursuant to Court orders or on the Directions issued by the Department of Telecommunications',

    'IQ'  : u'This Website has been blocked by the iraqi ministry of communications.</p>',
    'KW'  : u'<img src=\"images/eng2.png\" width=\"386\" height=\"98\" />',
    'LY'  : u'onclick=\"emailForm();\">filter@ltt.ly</a></p>',

    'PK1' : u'to access contains content that is prohibited for viewership from within',
    'PK2' : u'The site you are trying to access contains content that is&nbsp;prohibited for viewership from within Pakistan.</span>',
    'PK3' : u'<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEU',

    'QA'  : u'<img src=\"http://censor.qa/message5.jpg\">',

    'RU4' : u'<p>This site (<b></b>) is blocked by a public authority according to the legislation of the Russian Federation.</p>',
    'RU5' : u'Запрет доступа - Москва и Подмосковье',
    'RU6' : u'<p>Доступ к запрашиваемому Вами Интернет-ресурсу ограничен по требованию правоохранительных органов в соответствии с законодательством и/или на основании решения суда.</p>',
    'RU7' : u'<h5>Ссылка заблокирована по решению суда</h5',
    'RU8' : u'<a href=\"http://minjust.ru/ru/extremist-materials\" rel=\"nofollow\">',
    'RU9' : u'соответствии с требованиями Законодательства Российской Федерации.',


    'SA'  : u'If you believe the requested page should not be blocked please <a href=\"http://www.internet.gov.sa/resources/block-unblock-request/',


    'SD'  : u'href=\"mailto:filtering@ntc.gov.sd',

    'UK2' : u'This site has been blocked by BT Parental Controls.</div>',
    'UK3' : u'<p>BSkyB is required by Court order to prevent access to this site in order to help protect against copyright infringement.</p>',

    'YE1' : u'fenet@yemen.net.ye\">here</a> if you require access to this website or you have any additional websites that should be blocked due to its inappropriate content.</span>',
    'YE2' : u'If you feel this website should be opened, <br />please&nbsp; <a href=\"mailto:safenet@yemen.net',

    #Quack's Regexes
    'AR'  : u'Web Bloqueada!</title>',
    'AR2_US' : u'<title>Página Web Bloqueada!',

    'BE_CN_MY_NO_KR_ES_TW_TH_TR_US'  : u'<p>Access to the web page you were trying to visit has been blocked in accordance with company policy. Please contact your system administrator if you believe this is in error.</p>',
    'BR'  : u'Violação nas aplicações controladas',
    'BR_EG_GR_HK_IN_JP_MX_PL_KR_SG_ES_TW_TH_US'    : u'/XX/YY/ZZ/CI/MGPGHGPGPFGHCDPFGGOGFGEH',
    'BR_HK_IN_MX_TH_JP' : u'<title>Web Filter Violation</title>',
    'BR_TW_US_HK_ES_IN_JP_KR_MX_PL_SG' : u'<title>Application Control Violation</title>',
    'EG_IN' : u'Application Control Violation',
    'CA'  : u'You attempted to access a site that is against the Acceptable Use Policy, or has a reputation for hosting Malware that could infect your computer and steal your information. Please visit our <a href="http://ishare.novachem.co',
    'CA1' : u'<title>Defense Center Blocked Message</title>',
    'CA_RU_SE_TW_US' : u'<strong>You are attempting to access a forbidden site.</strong>',

    'CL'   : u'http://186.103.236.197:8183/redirect.cgi?',
    'CN1'  : u'var u=\"https://n.dafa014.vip/',
    'CN2'  : u'http://222.135.125.13/disable/disable.htm',
    'CN3'  : u'<title>您正在访问恶意网页</title>',
    'CN4'  : u'<title>NetentSec Content Filter - Access Denied</title>',
    'CN5'  : u'the request has been blocked<br><br>matched config:<br>policy name',
    'CN6'  : u'<p>Sorry, but the URL you\'r requesting is prohibited!</p>',
    'CN7'  : u'Location: http://obdavidbeckham.99wwl.com',
    'CN8'  : u'Location: http://ofdskkkjnnhvvbbn-nmg4q.5000299.com',
    'CN9'  : u'Location: https://xianlu666666666666666.bytycgogo5.com',
    'CN10' : u'Location: http://121.201.80.216:9000',
    'CN11' : u'Location: http://edong.com/block/error.html',
    'CN12' : u'Location: http://www.dns.gd.cn/index.html',
    'CN13' : u'Location: https://www.linktom.com/ba/ba.html',
    'CN14' : u'Location: http://activity.biggeryun.com/Intercept',
    'CN15' : u'https://dnspod.qcloud.com/static/block.html',
    'CN16' : u'Location: http://ai.taobao.com?pid=mm_34939156_18524743_65556322',
    'CN17' : u'http://114.115.192.242:9080/error.html',
    'CN18' : u'因该网站未进行备案或涉及发布违禁信息，违反工信部、公安部相关规定而无法访问。',
    'CN19' : u'src=\"http://zd.ywfscdn.com\"></iframe><',
    'CN20' : u'http://42.159.191.244:5671/lan',
    'CN21' : u'<title>未备案等原因无法访问</title>',
    'CN22' : u'http://220.231.20.138:9080/error.html',
    'CN23' : u'当前页面包含敏感关键字词，请与管理员联系!',
    'CN24' : u'您的域名因未取得工信部网站备案号，按照工信部33号令屏蔽访问。请您办理工信部网站备案，取得网站备案号后恢复访问。',
    'CN25' : u'页面包含敏感关键字词 或者 域名没有备案号！',
    'CN26' : u'您可能因为上网制度没有权限访问此网页。请与网络管理员联系。',
    'CN27' : u'域名在访问黑名单中。',
    'CN28' : u'src=\'http://www.linktom.com/ba/ba.html',

    'CO'   : u'Location: http://186.179.96.84/coljuegos.html',
    'CO2'  : u'Location: http://190.6.160.34',
    'CO3'  : u'Location: http://www.coljuegos.gov.co/publicaciones/301824',

    'EC1'  : u'<h1>Por tu seguridad la p&aacute;gina web ha sido bloqueada</h1>',
    'EC2_TW_TH_US_BE_CN_ES'  : u'<title>Web Page Blocked</title>',

    'HK'   : u'Access to this malicious web site from HKUST has been blocked by ITSC for your protection.',
    'CA_CN_IN_RU_SE_TH_TW_US'  : u'<title>Access Denied</title>',
    'HU'   : u'Location:  http://213.14.227.50/landpage',

    'IN8'  : u'Access Denied as per DOT/TRAI Guidelines - By Order ',
    'IN9'  : u'<p>The access to this site is prohibited as per instructions from Authority(s)/Honorable Court Order</p>',
    'IN10' : u'<H1>Access to this URL is denied</H1>',
    'IN11' : u'Location: http://192.168.1.1/UserCheck/PortalMain?IID=',
    'IN12' : u'href=\"MSecure_WebSecurit_block_files',
    'IN13_PL' : u'<title>Application Blocked!</title>',
    'IR3'  : u'href="http://10.104.15.24/?msisdn',

    'IT2'  : u'Location:http://www.comeser.com/aams.html',

    'JP_TW_TH_TR'   : u'<p>Access to the application you were trying to use has been blocked in accordance with company policy.',

    'KZ'   : u'http://185.100.67.39/?hizb-ut-tahrir.',

    'MY2'  : u'src=\"http://113.23.183.146/disable/disable.htm',

    'MX_MN_TH' : u'/UserCheck/PortalMain',

    'NL_RU': u'http://vasexperts.ru/test/blocked.php',

    'NG'   : u'http://portal.swiftng.com/',

    'NO_ES' : u'php/urlblock.php?vsys=1&cat=',

    'PK4'  : u'http://restrictk.wateen.net/?',
    'PK5'  : u'http://restrict.wateen.net/restrict/',

    'PL_US'   : u'<title>Web Page Blocked!</title>',
    'PL'   : u'<title>Warning!</title>',

    'RU10' : u'http://forbidden.local/index.ph',
    'RU11' : u'http://zapret.2090000.ru',
    'RU12' : u'http://211.ru/149.html',
    'RU13' : u'http://block.tomtel.ru/block.html',
    'RU14' : u'http://detect-web.signaltv.net/3',
    'RU15' : u'http://out-of-service.planeta.tc',
    'RU16' : u'http://site-blocked.ru',
    'RU17' : u'https://lk.goodline.info/middlestatus.html',
    'RU18' : u'http://stub.dianet.ru/forbidden/',
    'RU19' : u'http://www.kristel.ru/?mode=zapret',
    'RU20' : u'http://zapret-info.b2b.at-home.ru/',
    'RU21' : u'Location: http://zapret-info.dsi.ru',
    'RU22' : u'Location: http://billing.spb.rsvo.ru/blocked/blocked.html',
    'RU23' : u'Location: http://blackhole.piter-telecom.ru',
    'RU24' : u'Location: http://blacklist.schelkovo-net.ru',
    'RU25' : u'Location: http://block.itnet33.ru/info/forbiddens.php',
    'RU26' : u'Location: http://block.msk.avantel.ru',
    'RU27' : u'Location: http://blockpage.kmv.ru',
    'RU28' : u'Location: http://block.rosintel.tk/',
    'RU29' : u'Location: http://block.westlan.ru',
    'RU30' : u'Location: http://close.g-service.ru/access_denied_op.html',
    'RU31' : u'Location: http://hold.taiget.ru/block',
    'RU32' : u'Location: http://redirects.tvhost.ru',
    'RU33' : u'Location: https://07.altegrosky.ru/180.html',
    'RU34' : u'Location: http://secure.weba.ru/index.php?block=',
    'RU35' : u'Location: https://redcom.ru/law/index.html',
    'RU36' : u'Location: http://stop.edpnet.net/ru-censored/',
    'RU37' : u'Location: http://www.it-grad.ru/blockpage.html',
    'RU38' : u'Location: http://www.skynet-kazan.com/_blocked.htm',
    'RU39' : u'Location: http://www.telemagadan.ru/bloked.php',
    'RU40' : u'Location: http://www.tmn.ru/cgi-bin/stub_html',
    'RU41' : u'Location: http://radugainternet.ru/kasat/access-error',
    'RU42' : u'Location: http://notify.bashtel.ru/block-rkn',
    'RU43' : u'Location: http://forbidden.yota.ru',


    'ES1' : u'<h1>URL bloqueada</h1>',
    'ES2' : u'<title>Acceso Bloqueado</title>',

    'TW1' : u'http://192.168.85.72/redirect/R50_GS.php',
    'TW2' : u'<title>Virus/Spyware Download Blocked</title>',
    'TW3' : u' http://tcsd.info',
    'TH11' : u'<p>The page you have requested has been blocked, because the URL is banned.</p>',
    'TW_JP' : u'<title>Application Blocked</title>',


    'TR7' : u'http://176.55.252.4:8080',
    'TR8' : u'http://195.175.254.2/?policyName=',
    'TR9' : u'policyName=BTK_FILTER',
    'TR10' : u'Location:  http://213.14.227.50/landpage',
    'TR11' : u'Location: http://46.196.235.106',
    'TR12'  : u'Location: http://88.255.216.16/landpage',
    'TR13' : u'http://aidiyet.esb.org.tr/',
    'TR14' : u'Location: http://bilgi.turktelekom.com.tr/guvenli_internet_uyari/index.html',
    'TR15' : u'http://guvenliinternet.turkcell.com.tr/cis/profil?CAT',
    'TR16': u'After technical analysis and legal consideration based on the law nr. 5651, administration measure',
    'UA1' : u'Location: http://rknblock.tscrimea.com',
    'UA2' : u'Location: http://rublacklist.sevstar.net',

    'US' : u'<title>Web Site Blocked</title>',
    'US2' :u'<strong>This site has been blocked by FOCUS Brands IT.</strong',

    'VE'  : u'8183/redirect.cgi',

    'VN'  : u'<H1>We\'re sorry but the page you\'re looking for could not be found...</H1>',

    # Zach's Blockpages
    'HU-Z1': u'Tájékoztatjuk a felhasználót, hogy a jelen honlapon közzétett tartalom, mint elektronikus hírközlő hálózat útján közzétett adat ideiglenes hozzáférhetetlenné tételét a Nemzeti Adó- és Vámhivatal',
    'HU-Z2' :u'Tájékoztatjuk a felhasználót, hogy a jelen honlapon közzétett tartalom, mint elektronikus hírközlő hálózat útján közzétett adat ideiglenes hozzáférhetetlenné tételét a Szerencsejáték Felügyelet',

    'IN-Z1' : u'<iframe src=\"http://restrictedurl.rcom.co.in/DOT-Deny-Page',
    'IN-Z2' : u'This URL has been blocked under instructions of a competent Government Authority or in compliance with the orders of a Court of competent jurisdiction',
    'IN-Z3' : u'This URL has been blocked under the instructions of the Competent Government Authority or in compliance with the orders of a Court of competent jurisdiction',
    'IN-Z4' : u'This URL has been blocked under Instructions of the Competent Goverment Authority or Incompliance to the orders of',
    'IN-Z5' : u'This website/url has been blocked under instructions of the Competent Government Authority or in compliance to the orders of',
    'IN-Z6' : u'URL or Domain you are trying to access is BLOCKED as per DoT Instructions',

    'IN-Z7' : u'The requested url is blocked, based on the blocking Instruction order received from the Department of Telecommunications',
    'IN-Z8' : u'404. That\'s an error.</font></h0>',
    'IN-Z9' : u'<HTML><BODY>HTTP Error 404 - File or Directory not found',
    'IN-Z10' : u'<h0><font color=\"black\">*“Error 403: Access Denied/Forbidden”*</font></h0>',
    'IN-Z11' : u'<html><body><h1>400 Bad request</h1>Your browser sent an invalid request.',
    'IN-Z12' : u'<html><body><h1>400 Bad request</h1>', #probably is too general
    'IN-Z13' : u'This website/URL has been blocked as per instructions from Department of Telecommunications of India.',
    'KR-Zguardian' : u'refresh\" content=\"0;url=\'https://guardian2.skbroadband.com?flag',
    'KR-Zuplu' : u'refresh\" content=\"0;url=\'http://cleanweb1.uplus.co.kr/kren?flag=',
    'KR-Z-songdo' : u'The requested web page is blocked by administrator.</span>',
    'KR-Z-surveillance' : u'<iframe id=\"f\"frameborder=\"0\"style=\"width:1;height:1\"></iframe><script>document.getElementById(\"f\").src',

    'RU-Z' : u'http://block.mts.ru/?host',
    'US-SA-AE-Z' : u'<title>Blocked URL</title><iframe frameborder=\'0\'',


    'IN-Z1' : u'Location: https://www.airtel.in/dot/?dpid',
    'RU-Z1' : u'Location: http://www.atlex.ru/block.html?url',
    'RU-Z2' : u'Location: https://www.atlex.ru/block.html?url',
    'RU-Z3' : u'Location: http://block.mts.ru/?host=',
    'RU-Z4' : u'Location: http://103.208.24.21/?catv0.42',
    'TR-Z1' : u'Location: http://195.175.254.2/'

    }


    blockpage_header_fingerprints = {
    'SA': ('Server', u'Protected by WireFilter'),
    'ID': ('Location', u'http://internet-positif.org'),
    'SD': ('Location', u'http://196.1.211.6:8080/alert/'),
    'QA': ('Location', u'http://www.vodafone.qa/alu.cfm'),
    'KR': ('Location', u'http://www.warning.or.kr'),
    'PT': ('Location', u'http://mobilegen.vodafone.pt/denied/dn'),
    'NO': ('Location', u'http://block-no.altibox.net/'),
    'UK': ('Location', u'http://blocked.nb.sky.com'),
    'RU': ('Location', u'http://warning.rt.ru'),
    'AE': ('Server', u'Protected by WireFilter'),

    'Q-RU21' : ('Location', u'http://zapret-info.dsi.ru'),
    'Q-RU22' : ('Location',u'http://billing.spb.rsvo.ru/blocked/blocked.html'),
    'Q-RU23' : ('Location',u'http://blackhole.piter-telecom.ru'),
    'Q-RU24' : ('Location',u'http://blacklist.schelkovo-net.ru'),
    'Q-RU25' : ('Location',u'http://block.itnet33.ru/info/forbiddens.php'),
    'Q-RU26' : ('Location',u'http://block.msk.avantel.ru'),
    'Q-RU27' : ('Location',u'http://blockpage.kmv.ru'),
    'Q-RU28' : ('Location',u'http://block.rosintel.tk/'),
    'Q-RU29' : ('Location',u'http://block.westlan.ru'),
    'Q-RU30' : ('Location',u'http://close.g-service.ru/access_denied_op.html'),
    'Q-RU31' : ('Location',u'http://hold.taiget.ru/block'),
    'Q-RU32' : ('Location',u'http://redirects.tvhost.ru'),
    'Q-RU33' : ('Location',u'https://07.altegrosky.ru/180.html'),
    'Q-RU34' : ('Location',u'http://secure.weba.ru/index.php?block='),
    'Q-RU35' : ('Location',u'https://redcom.ru/law/index.html'),
    'Q-RU36' : ('Location',u'http://stop.edpnet.net/ru-censored/'),
    'Q-RU37' : ('Location',u'http://www.it-grad.ru/blockpage.html'),
    'Q-RU38' : ('Location',u'http://www.skynet-kazan.com/_blocked.htm'),
    'Q-RU39' : ('Location',u'http://www.telemagadan.ru/bloked.php'),
    'Q-RU40' : ('Location',u'http://www.tmn.ru/cgi-bin/stub_html'),
    'Q-RU41' : ('Location',u'http://radugainternet.ru/kasat/access-error'),
    'Q-RU42' : ('Location',u'http://notify.bashtel.ru/block-rkn'),
    'Q-RU43' : ('Location',u'http://forbidden.yota.ru'),
    'Q-RU44' : ('Location',u'http://forbidden.local/index.php'),
    'Q-RU45' : ('Location',u'http://site-blocked.ru'),
    'Q-RU46' : ('Location' u'http://block.tomtel.ru/block.html'),
    'Q-CN7'  : ('Location', u'http://obdavidbeckham.99wwl.com'),
    'Q-CN8'  : ('Location', u'http://ofdskkkjnnhvvbbn-nmg4q.5000299.com'),
    'Q-CN9'  : ('Location', u'https://xianlu666666666666666.bytycgogo5.com'),
    'Q-CN10' : ('Location', u'http://121.201.80.216:9000'),
    'Q-CN11' : ('Location', u'http://edong.com/block/error.html'),
    'Q-CN12' : ('Location', u'http://www.dns.gd.cn/index.html'),
    'Q-CN13' : ('Location', u'https://www.linktom.com/ba/ba.html'),
    'Q-CN14' : ('Location', u'http://activity.biggeryun.com/Intercept'),
    'Q-CN16' : ('Location', u'http://ai.taobao.com?pid=mm_34939156_18524743_65556322'),

    'Q-CO'   : ('Location', u'http://186.179.96.84/coljuegos.html'),
    'Q-CO2'  : ('Location', u'http://190.6.160.34'),
    'Q-CO3'  : ('Location', u'http://www.coljuegos.gov.co/publicaciones/301824'),

    'Q-HU'   : ('Location', u'http://213.14.227.50/landpage'),

    'Q-IN11' : ('Location' , u'http://192.168.1.1/UserCheck/PortalMain?IID='),
    'Q-IT2'  : ('Location' , u'http://www.comeser.com/aams.html'),

    'Q-TR10' : ('Location',  u'http://213.14.227.50/landpage'),
    'Q-TR11' : ('Location', u'http://46.196.235.106'),
    'Q-TR12'  : ('Location', u'http://88.255.216.16/landpage'),
    'Q-TR14' : ('Location', u'http://bilgi.turktelekom.com.tr/guvenli_internet_uyari/index.html'),
    'Q-UA1' : ('Location', u'http://rknblock.tscrimea.com'),
    'Q-UA2' : ('Location', u'http://rublacklist.sevstar.net'),

    'Q-JP' : ('Location', u'http://www.cleanjapan.info/Okayama/notice.html'),
    'Q-BE'  : ('Location', u'http://telegate.telenet.be/telegate/warning.html'),
    'IN-Z1' : ('Location', u'https://www.airtel.in/dot/?dpid'),
    'RU-Z1' : ('Location', u'http://www.atlex.ru/block.html?url'),
    'RU-Z2' : ('Location', u'https://www.atlex.ru/block.html?url'),
    'RU-Z3' : ('Location', u'http://block.mts.ru/?host='),
    'RU-Z4' : ('Location', u'http://103.208.24.21/?catv0.42'),
    'TR-Z1' : ('Location', u'http://195.175.254.2/'),

    }
    block_page_regs = ["src=[\",\']http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:\:[0-9]{2,5})?"
                       "/webadmin/deny/",
                       "src=[\",\']http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:\:[0-9]{2,5})?"
                       "/blocked.html",
                       "The url has been blocked",
            "powered      (?:\s+|<[^>]+>)* by           (?:\s+|<[^>]+>)* sify         (?:\s+|<[^>]+>)*", # not a good regex, needs powered by as well
            "cleanconnect (?:\s+|<[^>]+>)*"
            ]
    if body is not None:
    for regex in block_page_regs:
        #logging.info(str(regex))
            if re.search(regex, body):
        comments['reason'].append("HTTP body matches pattern [%s]" %regex)
    if header is not None:
    for country, fp in blockpage_header_fingerprints.items():
        #logging.info('header %s' %(str(fp)))
            if fp[0] in header and fp[1] in header[fp[0]]:
        logging.info("this url had sth in its header")
        comments['reason'].append("HTTP header field [%s] contains [%s]" %(fp[0], fp[1]))
        # search all matched regeexs
            # return True
    if body is not None:
        for country, fp in blockpage_body_fingerprints.items():
            if fp in body:
        comments['reason'].append("HTTP body contains [%s]" %(fp))
        # search all bodies
            #return True
    logging.info('returning blockpage check')
    return comments

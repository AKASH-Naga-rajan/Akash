FN_INSTALLDIR()
{
source ./config.txt
if [ "$RPICAMDIR" == "" ]; then
  INSTALLDIR="$WWWROOT"
else
  INSTALLDIR="$WWWROOT/$RPICAMDIR"
fi
}
FN_INSTALLDIR

# Tedect Debian version (we not using that right now. Historical, maby we can use)
DEBVERSION=$(cat /etc/issue)
if [ "$DEBVERSION" == "Raspbian GNU/Linux 7 \n \l" ]; then
  echo "Raspbian Wheezy";
  #WWWROOT="/var/www"
elif [ "$DEBVERSION" == "Raspbian GNU/Linux 8 \n \l" ]; then
  echo "Raspbian Jessie";
  #WWWROOT="/var/www/html"
else
  echo "Unknown"
  #WWWROOT="/var/www"
fi

# -------------------------------- START/FUNCTIONS --------------------------------	
FN_STOP ()
{ # This is function stop
        sudo killall raspimjpeg
        sudo killall php
        sudo killall motion
        sudo service apache2 stop >/dev/null 2>&1
        sudo service nginx stop >/dev/null 2>&1
        dialog --title 'Stop message' --infobox 'Stopped.' 4 16 ; sleep 2
}

FN_REBOOT ()
{ # This is function reboot system
  dialog --title "You must reboot your system!" --backtitle "$backtitle" --yesno "Do you want to reboot now?" 5 33
  response=$?
    case $response in
      0) sudo reboot;;
      1) dialog --title 'Reboot message' --colors --infobox "\Zb\Z1"'Pending system changes that require a reboot!' 4 28 ; sleep 2;;
      255) dialog --title 'Reboot message' --colors --infobox "\Zb\Z1"'Pending system changes that require a reboot!' 4 28 ; sleep 2;;
    esac
}

FN_ABORT()
{
    $color_red; echo >&2 '
***************
*** ABORTED ***
***************
'
    echo "An error occurred. Exiting..." >&2; $color_reset
    exit 1
}

FN_RPICAMDIR ()
{ 
  source ./config.txt
  
  tmpfile=$(mktemp)
  dialog  --backtitle "$backtitle" --title "Default www-root is $WWWROOT" --cr-wrap --inputbox "\
  Current install path is $WWWROOT/$RPICAMDIR
  Enter new install Subfolder if you like." 8 52 $RPICAMDIR 2>$tmpfile
			
  sel=$?
			
  RPICAMDIR=`cat $tmpfile`
  case $sel in
  0)
    sudo sed -i "s/^RPICAMDIR=.*/RPICAMDIR=\"$RPICAMDIR\"/g" ./config.txt	
  ;;
  1) source ./config.txt ;;
  255) source ./config.txt ;;
  esac

  dialog --title 'Install path' --infobox "Install path is set $WWWROOT/$RPICAMDIR" 4 48 ; sleep 3
  sudo chmod 664 ./config.txt

  if [ "$DEBUG" == "yes" ]; then
    dialog --title "FN_RPICAMDIR ./config.txt contains" --textbox ./config.txt 22 70
  fi
}

FN_APACHEPORT ()
{
  source ./config.txt
		
  if [ "$WEBPORT" == "" ]; then
    WEBPORT=$(cat $APACHEDEFAULT | grep "<VirtualHost" | cut -d ":" -f2 | cut -d ">" -f1)
    sudo sed -i "s/^WEBPORT=.*/WEBPORT=\"$WEBPORT\"/g" ./config.txt
  fi		
		
  tmpfile=$(mktemp)
  dialog  --backtitle "$backtitle" --title "Current Apache web server port is $WEBPORT" --inputbox "Enter new port:" 8 40 $WEBPORT 2>$tmpfile
			
  sel=$?
			
  WEBPORT=`cat $tmpfile`
  case $sel in
  0)
    sudo sed -i "s/^WEBPORT=.*/WEBPORT=\"$WEBPORT\"/g" ./config.txt	
  ;;
  1) source ./config.txt ;;
  255) source ./config.txt ;;
  esac
			
  tmpfile=$(mktemp)
  sudo awk '/NameVirtualHost \*:/{c+=1}{if(c==1){sub("NameVirtualHost \*:.*","NameVirtualHost *:'$WEBPORT'",$0)};print}' /etc/apache2/ports.conf > "$tmpfile" && sudo mv "$tmpfile" /etc/apache2/ports.conf
  sudo awk '/Listen/{c+=1}{if(c==1){sub("Listen.*","Listen '$WEBPORT'",$0)};print}' /etc/apache2/ports.conf > "$tmpfile" && sudo mv "$tmpfile" /etc/apache2/ports.conf
  sudo awk '/<VirtualHost \*:/{c+=1}{if(c==1){sub("<VirtualHost \*:.*","<VirtualHost *:'$WEBPORT'>",$0)};print}' $APACHEDEFAULT > "$tmpfile" && sudo mv "$tmpfile" $APACHEDEFAULT
  if [ ! "$RPICAMDIR" == "" ]; then
    if [ "$WEBPORT" != "80" ]; then
      sudo sed -i "s/^netcam_url.*/netcam_url\ http:\/\/localhost:$WEBPORT\/$RPICAMDIR\/cam_pic.php/g" /etc/motion/motion.conf
    else
      sudo sed -i "s/^netcam_url.*/netcam_url\ http:\/\/localhost\/$RPICAMDIR\/cam_pic.php/g" /etc/motion/motion.conf
    fi
  else
    if [ "$WEBPORT" != "80" ]; then
      sudo sed -i "s/^netcam_url.*/netcam_url\ http:\/\/localhost:$WEBPORT\/cam_pic.php/g" /etc/motion/motion.conf
    else
      sudo sed -i "s/^netcam_url.*/netcam_url\ http:\/\/localhost\/cam_pic.php/g" /etc/motion/motion.conf
    fi
  fi
  sudo chown motion:www-data /etc/motion/motion.conf
  sudo chmod 664 /etc/motion/motion.conf
  sudo service apache2 restart
}

FN_SECURE_APACHE_NO ()
{
  if [ "$DEBUG" == "yes" ]; then
    dialog --title 'FN_SECURE_APACHE_NO' --infobox 'FN_SECURE_APACHE_NO STARTED.' 4 25 ; sleep 2
  fi
  #APACHEDEFAULT="/etc/apache2/sites-available/default"
  if [ "$APACHEDEFAULT" == "/etc/apache2/sites-available/default" ]; then
    tmpfile=$(mktemp)
    sudo awk '/AllowOverride/{c+=1}{if(c==2){sub("AllowOverride.*","AllowOverride None",$0)};print}' $APACHEDEFAULT > "$tmpfile" && sudo mv "$tmpfile" $APACHEDEFAULT
  elif [ "$APACHEDEFAULT" == "/etc/apache2/sites-available/000-default.conf" ]; then	
    tmpfile=$(mktemp)
    sudo awk '/AllowOverride/{c+=1}{if(c==3){sub("AllowOverride.*","AllowOverride None",$0)};print}' /etc/apache2/apache2.conf > "$tmpfile" && sudo mv "$tmpfile" /etc/apache2/apache2.conf
  else
    echo "$(date '+%d-%b-%Y-%H-%M') Disable security is not possible in apache conf!" >> ./error.txt
  fi	
  #sudo awk '/netcam_userpass/{c+=1}{if(c==1){sub("^netcam_userpass.*","; netcam_userpass value",$0)};print}' /etc/motion/motion.conf > "$tmpfile" && sudo mv "$tmpfile" /etc/motion/motion.conf
  sudo sed -i "s/^netcam_userpass.*/; netcam_userpass value/g" /etc/motion/motion.conf
  sudo /etc/init.d/apache2 restart
}

FN_SECURE_APACHE ()
{ # This is function secure in config.txt file. Working only apache right now! GUI mode.
source ./config.txt

FN_SECURE_APACHE_YES ()
{
  if [ "$DEBUG" == "yes" ]; then
    dialog --title 'FN_SECURE_APACHE_YES' --infobox 'FN_SECURE_APACHE_YES STARTED.' 4 25 ; sleep 2
  fi
  #APACHEDEFAULT="/etc/apache2/sites-available/default"
  if [ "$APACHEDEFAULT" == "/etc/apache2/sites-available/default" ]; then
    tmpfile=$(mktemp)
    sudo awk '/AllowOverride/{c+=1}{if(c==2){sub("AllowOverride.*","AllowOverride All",$0)};print}' $APACHEDEFAULT > "$tmpfile" && sudo mv "$tmpfile" $APACHEDEFAULT
  #APACHEDEFAULT="/etc/apache2/sites-available/000-default.conf"
  elif [ "$APACHEDEFAULT" == "/etc/apache2/sites-available/000-default.conf" ]; then
    tmpfile=$(mktemp)
    sudo awk '/AllowOverride/{c+=1}{if(c==3){sub("AllowOverride.*","AllowOverride All",$0)};print}' /etc/apache2/apache2.conf > "$tmpfile" && sudo mv "$tmpfile" /etc/apache2/apache2.conf
  else
    echo "$(date '+%d-%b-%Y-%H-%M') Enable security is not possible in apache conf!" >> ./error.txt
  fi 
  #sudo awk '/; netcam_userpass/{c+=1}{if(c==1){sub("; netcam_userpass.*","netcam_userpass '$user':'$passwd'",$0)};print}' /etc/motion/motion.conf > "$tmpfile" && sudo mv "$tmpfile" /etc/motion/motion.conf
  sudo sed -i "s/^; netcam_userpass.*/netcam_userpass/g" /etc/motion/motion.conf		
  sudo sed -i "s/^netcam_userpass.*/netcam_userpass $user:$passwd/g" /etc/motion/motion.conf
  sudo htpasswd -b -c /usr/local/.htpasswd $user $passwd
  sudo /etc/init.d/apache2 restart
}

# We make missing .htacess file
if [ ! -e $WWWROOT/$RPICAMDIR/.htaccess ]; then
sudo bash -c "cat > $WWWROOT/$RPICAMDIR/.htaccess" << EOF
AuthName "RPi Cam Web Interface Restricted Area"
AuthType Basic
AuthUserFile /usr/local/.htpasswd
AuthGroupFile /dev/null
Require valid-user
EOF
sudo chown -R www-data:www-data $WWWROOT/$RPICAMDIR/.htaccess
fi

exec 3>&1

dialog                                         \
--separate-widget $'\n'                        \
--title "RPi Cam Apache Webserver Security"    \
--backtitle "$backtitle"					   \
--form ""                                      \
0 0 0                                          \
"Enable:(yes/no)" 1 1   "$security" 1 18 15 0  \
"User:"           2 1   "$user"     2 18 15 0  \
"Password:"       3 1   "$passwd"   3 18 15 0  \
2>&1 1>&3 | {
    read -r security
    read -r user
    read -r passwd

if [[ ! "$security" == "" || ! "$user" == "" || ! "$passwd" == "" ]] ; then
  sudo sed -i "s/^security=.*/security=\"$security\"/g" ./config.txt
  sudo sed -i "s/^user=.*/user=\"$user\"/g" ./config.txt
  sudo sed -i "s/^passwd=.*/passwd=\"$passwd\"/g" ./config.txt
fi
}

exec 3>&-

source ./config.txt

if [ ! "$security" == "yes" ]; then
  FN_SECURE_APACHE_NO
  sudo sed -i "s/^security=.*/security=\"no\"/g" ./config.txt
else
  FN_SECURE_APACHE_YES
fi

sudo chown motion:www-data /etc/motion/motion.conf
sudo chmod 664 /etc/motion/motion.conf
sudo chmod 664 ./config.txt
sudo service apache2 restart

if [ "$DEBUG" == "yes" ]; then
  if [ "$APACHEDEFAULT" == "/etc/apache2/sites-available/default" ]; then
    dialog --title "FN_SECURE_APACHE $APACHEDEFAULT contains" --textbox $APACHEDEFAULT 22 70
  elif [ "$APACHEDEFAULT" == "/etc/apache2/sites-available/000-default.conf" ]; then
    dialog --title "FN_SECURE_APACHE /etc/apache2/apache2.conf contains" --textbox /etc/apache2/apache2.conf 22 70    
  else
    echo "$(date '+%d-%b-%Y-%H-%M') Edit security is not possible in apache conf!"
  fi
  dialog --title "FN_SECURE_APACHE /etc/motion/motion.conf contains" --textbox /etc/motion/motion.conf 22 70
  dialog --title "FN_SECURE_APACHE ./config.txt contains" --textbox ./config.txt 22 70
fi
}

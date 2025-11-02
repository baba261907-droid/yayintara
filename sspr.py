import requests
import re
import os

REDIRECT_PAGE = "https://www.selcuksportshd.is/"
channel_ids = [
    "selcukbeinsports1", "selcukbeinsports2", "selcukbeinsports3",
    "selcukbeinsports4", "selcukbeinsports5", "selcukbeinsportsmax1",
    "selcukbeinsportsmax2", "selcukssport", "selcukssport2",
    "selcuksmartspor", "selcuksmartspor2", "selcuktivibuspor1",
    "selcuktivibuspor2", "selcuktivibuspor3", "selcuktivibuspor4",
    "selcukbeinsportshaber", "selcukaspor", "selcukeurosport1",
    "selcukeurosport2", "selcuksf1", "selcuktabiispor", "ssportplus1"
]

def get_active_domains():
    print("🌐 Yönlendirme sayfası taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(REDIRECT_PAGE, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            found = re.findall(r'https://www\.selcuksportshd[0-9a-z\-]+\.xyz/', r.text)
            return list(set(found))
    except Exception as e:
        print(f"❌ Hata: {e}")
    return []

def find_working_domain(domains):
    headers = {"User-Agent": "Mozilla/5.0"}
    for domain in domains:
        try:
            print(f"🧭 Deneniyor: {domain}")
            r = requests.get(domain, headers=headers, timeout=10, verify=False)
            if r.status_code == 200 and "uxsyplayer" in r.text:
                print(f"✅ Aktif yayın domaini bulundu: {domain}")
                return r.text, domain
        except:
            continue
    print("⛔ Uygun domain bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    return f"https://{match.group(1)}" if match else None

def extract_base_stream_url(html):
    match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', html)
    return match.group(1) if match else None

def build_m3u8_links(base_stream_url, channel_ids):
    return [(cid, f"{base_stream_url}{cid}/playlist.m3u8") for cid in channel_ids]

def write_m3u_file(m3u8_links, filename="selcuksport.m3u", referer=""):
    os.makedirs("Kanallar", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in m3u8_links:
            f.write(f"#EXTINF:-1,{name}\n")
            f.write("#EXTVLCOPT:http-user-agent=Mozilla/5.0\n")
            f.write(f"#EXTVLCOPT:http-referrer={referer}\n")
            f.write(f"{url}\n")
    print(f"✅ M3U dosyası oluşturuldu: {filename}")

# Ana işlem
if __name__ == "__main__":
    print("🚀 Yayınları Tara ve M3U Oluştur Başladı")
    domains = get_active_domains()
    html, referer_url = find_working_domain(domains)

    if html:
        stream_domain = find_dynamic_player_domain(html)
        if stream_domain:
            try:
                r = requests.get(f"{stream_domain}/index.php?id={channel_ids[0]}", headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": referer_url
                }, timeout=10, verify=False)
                base_url = extract_base_stream_url(r.text)
                if base_url:
                    m3u_links = build_m3u8_links(base_url, channel_ids)
                    write_m3u_file(m3u_links, referer=referer_url)
                    print(f"\n🎉 Tamamlandı! Toplam {len(m3u_links)} kanal eklendi.")
                else:
                    print("❌ Yayın URL'si bulunamadı.")
            except Exception as e:
                print(f"⚠️ Yayın bilgisi alınırken hata: {e}")
        else:
            print("❌ Yayın sunucusu bulunamadı.")
    else:
        print("⛔ Hiçbir domain'e erişilemedi.")

# -*- coding: iso-8859-1 -*-
# Copyright (c) 2017 Jamie Bull - oCo Carbon Ltd
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================

import os
import requests
from platform import system
import re
import subprocess
import time


class MyWigleClient:
    """
    Wrapper for Wigle API: search, statistic, uploads, profile, sniffer.
    """

    def __init__(self, user: str, key: str):
        self.user = user
        self.key = key
        self.url = "https://api.wigle.net/api/v2/{section}/{endpoint}"
        self.auth = requests.auth.HTTPBasicAuth(self.user, self.key)
        if self.user == "" or self.key == "":
            print(
                "Besuche https://wigle.net/account, um deinen API-Token zu holen und ihn hier einzutragen."
            )

    # ---- HTTP-Methods ----
    def _get(self, section, endpoint, **kwargs):
        path = self.url.format(section=section, endpoint=endpoint)
        r = requests.get(path, auth=self.auth, params=kwargs)
        r.raise_for_status()
        return r.json()

    def _post(self, section, endpoint, **kwargs):
        path = self.url.format(section=section, endpoint=endpoint)
        r = requests.post(path, auth=self.auth, params=kwargs)
        r.raise_for_status()
        return r.json()

    # ---- Network-Funktions ----
    def network_comment(self, netid, comment):
        return self._post("network", "comment", netid=netid, comment=comment)

    def network_detail(
        self,
        netid=None,
        operator=None,
        lac=None,
        cid=None,
        system=None,
        network=None,
        basestation=None,
    ):
        return self._get(
            "network",
            "detail",
            netid=netid,
            operator=operator,
            lac=lac,
            cid=cid,
            system=system,
            network=network,
            basestation=basestation,
        )

    def network_geocode(self, addresscode=None):
        return self._get("network", "geocode", addresscode=addresscode)

    def network_search(
        self,
        onlymine=None,
        first=None,
        latrange1=None,
        latrange2=None,
        longrange1=None,
        longrange2=None,
        lastupdt=None,
        freenet=None,
        paynet=None,
        netid=None,
        ssid=None,
        ssidlike=None,
        variance=None,
        resultsPerPage=None,
    ):
        return self._get(
            "network",
            "search",
            onlymine=onlymine,
            first=first,
            latrange1=latrange1,
            latrange2=latrange2,
            longrange1=longrange1,
            longrange2=longrange2,
            lastupdt=lastupdt,
            freenet=freenet,
            paynet=paynet,
            netid=netid,
            ssid=ssid,
            ssidlike=ssidlike,
            variance=variance,
            resultsPerPage=resultsPerPage,
        )

    # ---- statistics ----
    def stats_countries(self):
        return self._get("stats", "countries")

    def stats_general(self):
        return self._get("stats", "general")

    def stats_group(self):
        return self._get("stats", "group")

    def stats_regions(self, country=None):
        return self._get("stats", "regions", country=country)

    def stats_site(self):
        return self._get("stats", "site")

    def stats_standings(self, sort=None, pagestart=None, pageend=None):
        return self._get(
            "stats", "standings", sort=sort, pagestart=pagestart, pageend=pageend
        )

    def stats_user(self):
        return self._get("stats", "user")

    # ---- FileUploads ----
    def file_kml(self, transid):
        endpoint = f"kml/{transid}"
        return self._get("file", endpoint)

    def file_transactions(self, pagestart=None, pageend=None):
        return self._get("file", "transactions", pagestart=pagestart, pageend=pageend)

    def file_upload(self, file, donate=None):
        # file must be a File-Objekt
        files = {"file": file}
        params = {}
        if donate is not None:
            params["donate"] = donate
        path = self.url.format(section="network", endpoint="upload")
        r = requests.post(path, auth=self.auth, files=files, data=params)
        r.raise_for_status()
        return r.json()

    # ---- Profile ----
    def profile_apiToken(self, token_type=None):
        params = {"type": token_type} if token_type else {}
        return self._get("profile", "apiToken", **params)

    def profile_user(self):
        return self._get("profile", "user")

    # ---- Sniffer (local WiFi-Analysis) ----
    def sniffer_local_bssids(self):
        scan_cmd = {
            "windows": "netsh wlan show networks mode=Bssid",
            "linux": "nmcli -t -f bssid dev wifi list",
            "darwin": "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s",
        }
        sysname = system().lower()
        cmd = scan_cmd.get(sysname)
        if not cmd:
            raise Exception("system not supported for WiFi scan!")
        res = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        pattern = re.compile(r"(?:[0-9a-fA-F]:?){12}")
        bssids = pattern.findall(res)
        return set(bssids)

    def sniffer_geolocate(self, geocoder="wigle"):
        lats = []
        longs = []
        for bssid in self.sniffer_local_bssids():
            print("BSSID:", bssid)
            if geocoder == "wigle":
                lat, lng = self.sniffer_geolocate_wigle(bssid)
            elif geocoder == "google":
                lat, lng = self.sniffer_geolocate_google(bssid)
            else:
                lat, lng = None, None
            print(lat, lng)
            if lat:
                lats.append(lat)
            if lng:
                longs.append(lng)
            time.sleep(0.1)
        if lats:
            lat = sum(lats) / len(lats)
            lng = sum(longs) / len(longs)
            return lat, lng
        else:
            return "No Geolocalisation possible"

    def sniffer_geolocate_wigle(self, bssid):
        res = self.network_search(netid=bssid)
        if res.get("success") and res.get("resultCount"):
            lat = res["results"][0]["trilat"]
            lng = res["results"][0]["trilong"]
        else:
            print(res)
            lat, lng = None, None
        return lat, lng

    def sniffer_geolocate_google(self, bssid):
        geolocate_cmd = "https://maps.googleapis.com/maps/api/browserlocation/json?browser=firefox&wifi=mac:{bssid}"
        res = requests.get(geolocate_cmd.format(bssid=bssid))
        res.raise_for_status()
        res = res.json()
        if res.get("status") == "OK":
            lat = res["location"]["lat"]
            lng = res["location"]["lng"]
        else:
            lat, lng = None, None
        return lat, lng

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from ttkthemes import ThemedStyle 
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import requests
import threading
import json
import os
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from pymongo import MongoClient
import csv

class DarkWebScraperTool:
    def __init__(self, master):
        self.master = master
        master.title("Dark Web Scraper Tool")
        self.style = ttk.Style(master)
        self.style = ThemedStyle(master)
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.theme_use('clam') 
        master.configure(bg="#2E2E2E")

        self.url_entry = ttk.Entry(master, width=40)
        self.url_entry.grid(row=0, column=0, padx=10, pady=10)

        self.add_button = ttk.Button(master, text="Add", command=self.add_site)
        self.add_button.grid(row=0, column=1, padx=10, pady=10)

        self.analyze_button = ttk.Button(master, text="Scrape", command=self.scrape_and_analyze)
        self.analyze_button.grid(row=0, column=2, padx=10, pady=10)

        self.list_button = ttk.Button(master, text="Added Sites", command=self.list_sites)
        self.list_button.grid(row=0, column=3, padx=10, pady=10)

        self.clear_button = ttk.Button(master, text="Clear", command=self.clear_text)
        self.clear_button.grid(row=0, column=4, padx=10, pady=10)

        # Output text box for listed sites
        self.listed_sites_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=20)
        self.listed_sites_text.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')
        
        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=20)
        self.output_text.grid(row=1, column=0, columnspan=5, padx=10, pady=10)
        # Output text box for analyzed data
        self.analyzed_data_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=100, height=20)
        self.analyzed_data_text.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')
        self.analyzed_data_text.grid_remove()  # Hide initially
         
        self.clear_button = ttk.Button(master, text="Clear", command=self.clear_text)
        self.clear_button.grid(row=0, column=4, padx=10, pady=10)
        self.onion_sites = []
        self.site_data = {}
        self.scraping_enabled = False  # Variable to control automatic scraping

        # Load saved data
        self.load_data()

    def add_site(self):
        dark_web_url = self.url_entry.get().strip()
        if not dark_web_url.startswith('http://') and not dark_web_url.startswith('https://'):
            dark_web_url = 'http://' + dark_web_url

        if dark_web_url not in self.onion_sites:
            self.onion_sites.append(dark_web_url)
            self.url_entry.delete(0, tk.END)
            self.save_data()
            if self.scraping_enabled:
              threading.Thread(target=self.scrape_and_analyze, args=(dark_web_url,), daemon=True).start()
    def analyze(self):
        # Analyze data for all onion sites only if scraping is enabled
        if self.scraping_enabled:
            for dark_web_url in self.onion_sites:
                threading.Thread(target=self.scrape_and_analyze, args=(dark_web_url,), daemon=True).start()
    def scrape_and_analyze(self, dark_web_url):
        try:
            tor_proxy = {
                'http': 'socks5h://127.0.0.1:9150',
                'https': 'socks5h://127.0.0.1:9150',
            } 
            time.sleep(30)
            response = requests.get(dark_web_url, proxies=tor_proxy)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            div_tags = soup.find_all('div')

            data = []
            for div_tag in div_tags:
                text_content = div_tag.get_text(separator='\n').strip()
                data.append(text_content)

            # Store the analyzed data in the dictionary
            self.site_data[dark_web_url] = {'timestamp': datetime.now().isoformat(), 'data': data}

            # Update the GUI with the results if clicked from "List Sites"
            if dark_web_url in self.onion_sites:
                analyzed_data = "\n".join(data)
                self.master.after(0, self.display_result, dark_web_url, analyzed_data)

            self.save_data()

        except RequestException as e:
            error_message = f"Error: {e}"
            self.master.after(0, self.display_result, dark_web_url, error_message)
    def scrape_specific_url(self,dark_web_url):
        tor_proxy = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150',
    }
        retries = Retry(total=5, backoff_factor=10, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)

    # Connect to MongoDB
        

        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'c32zjeghcp5tj3kb72pltz56piei66drc63vkhn5yixiyk4cmerrjtid.onion',
        'Upgrade-Insecure-Requests': '1',
     }

        with requests.Session() as session:
          session.mount('http://', adapter)
          session.mount('https://', adapter)

          try:
             response = requests.get(dark_web_url, proxies=tor_proxy, headers=headers)
             response.raise_for_status()

            # Parse HTML using BeautifulSoup
             soup = BeautifulSoup(response.text, 'html.parser')

            # Find all div tags and extract text content
             data=[]
             div_tags = soup.find_all('div')
             for div_tag in div_tags:
                text_content = div_tag.get_text(separator='\n').strip()
                data.append(text_content)
                # Only print non-empty lines without whitespace characters
                
                self.site_data[dark_web_url] = {'timestamp': datetime.now().isoformat(), 'data': data}

            # Update the GUI with the results if clicked from "List Sites"
                if dark_web_url in self.onion_sites:
                       analyzed_data = "\n".join(data)
                       self.master.after(0, self.display_result, dark_web_url, analyzed_data)

                self.save_data()
          

          except RequestException as e:
            error_message = f"Error: {e}"
            self.master.after(0, self.display_result, dark_web_url, error_message)
          
    def list_sites(self):
    # Clear the listed sites text box
      self.output_text.delete(1.0, tk.END)
      
      for site in self.onion_sites:
        # Bind the click event for each site
        self.output_text.tag_config(site, underline=True, foreground="blue")                           
        self.output_text.insert(tk.END, f"{site}  ", site)
        self.output_text.tag_bind(site, "<Button-1>", lambda event, site=site: self.click_site(site))
        self.output_text.tag_bind(site, "<Enter>", lambda event, site=site: self.output_text.config(cursor="hand2"))
        self.output_text.tag_bind(site, "<Leave>", lambda event, site=site: self.output_text.config(cursor=""))

        # Add a delete option for each site
        delete_button = tk.Button(self.output_text, text="Delete", command=lambda site=site: self.delete_site(site), cursor='hand2', width=8,height=1)
        self.output_text.window_create(tk.END, window=delete_button)
        self.output_text.insert(tk.END, "\n")

    # If scraping is enabled, trigger scraping for all onion sites
      if self.scraping_enabled:
        self.analyze()


    # If scraping is enabled, trigger scraping for all onion sites
     

    def delete_site(self, dark_web_url):
    # Remove the selected site from the list and save data
     if dark_web_url in self.onion_sites:
        self.onion_sites.remove(dark_web_url)
        self.save_data()
        # Reload the updated list of sites
        self.list_sites()



    def click_site(self, dark_web_url):
        # Check if the site is already scraped, if not, trigger scraping
            # if dark_web_url ==  'http://cvz7ithpzhuptry4ulntqmd6edzycd5ed4lslfc5k6vnn3ragyky2zqd.onion/items/drugs ':
            #   threading.Thread(target=self.scrape_specific_url, daemon=True).start()
            # else:
              if dark_web_url == 'http://c32zjeghcp5tj3kb72pltz56piei66drc63vkhn5yixiyk4cmerrjtid.onion/forums':
                threading.Thread(target=self.scrape_specific_url, args=(dark_web_url,), daemon=True).start()
                analyzed_data = "\n".join(self.site_data[dark_web_url]['data'])
                self.display_result(dark_web_url, analyzed_data)
              else:
               if dark_web_url not in self.site_data and self.site_data:
                 threading.Thread(target=self.scrape_and_analyze, args=(dark_web_url,), daemon=True).start()
               else:
                analyzed_data = "\n".join(self.site_data[dark_web_url]['data'])
                self.display_result(dark_web_url, analyzed_data)
       

    def display_result(self, dark_web_url, result):
        # Display the analyzed data in the appropriate text box
        self.analyzed_data_text.delete(1.0, tk.END)
        self.analyzed_data_text.insert(tk.END, f"Analysis for {dark_web_url}:\n\n")
        self.analyzed_data_text.insert(tk.END, result)
        # Show the analyzed data text box
        self.analyzed_data_text.grid()

    def clear_text(self):
        # Clear both text boxes
        self.listed_sites_text.delete(1.0, tk.END)
        self.analyzed_data_text.delete(1.0, tk.END)

    def save_data(self):
        # Save the onion sites and their data
        data = {'onion_sites': self.onion_sites, 'site_data': self.site_data}
        with open('dark_web_data.json', 'w') as file:
            json.dump(data, file)

    def load_data(self):
        # Load saved data
        if os.path.exists('dark_web_data.json'):
            with open('dark_web_data.json', 'r') as file:
                data = json.load(file)
                self.onion_sites = data.get('onion_sites', [])
                self.site_data = data.get('site_data', {})

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkWebScraperTool(root)
    root.mainloop()

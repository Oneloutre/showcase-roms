"use client";


import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Smartphone, Cpu, Zap, Download, Github, Twitter, Menu, X, Mail, Copy } from 'lucide-react'
import Link from 'next/link'

import { FaTelegramPlane, FaPaypal, FaDiscord } from 'react-icons/fa'; // FontAwesome Telegram icon

function Paypal() {
    return (
        <div>
            <FaPaypal size={24} color="Purple-300" />
        </div>
    );
}

function Discord() {
  return (
      <div>
        <FaDiscord size={24} color="Purple-300" />
      </div>
  );
}

function Telegram() {
  return (
      <div>
        <FaTelegramPlane size={24} color="purple-300" />
      </div>
  );
}

export default function OnelotShowcaseRedesign() {
  const [activeTab, setActiveTab] = useState('official')
  const [menuOpen, setMenuOpen] = useState(false)

  const devices = {
    official: [
      { name: 'Xiaomi Mi Mix 2S', codename: 'polaris', image: 'https://raw.githubusercontent.com/Evolution-X/www_gitres/refs/heads/udc/devices/images/polaris.png', download:'https://sourceforge.net/projects/evolution-x/files/polaris' },
      { name: 'Google Pixel 3a', codename: 'sargo', image: 'https://raw.githubusercontent.com/Evolution-X/www_gitres/refs/heads/udc/devices/images/sargo.png', download:'https://sourceforge.net/projects/evolution-x/files/sargo' },
      { name: 'Google Pixel 3a XL', codename: 'bonito', image: 'https://raw.githubusercontent.com/Evolution-X/www_gitres/refs/heads/udc/devices/images/bonito.png', download:'https://sourceforge.net/projects/evolution-x/files/bonito'},
      { name: 'Google Pixel 3', codename: 'blueline', image: 'https://raw.githubusercontent.com/Evolution-X/www_gitres/refs/heads/udc/devices/images/blueline.png', download: 'https://sourceforge.net/projects/evolution-x/files/blueline' },
      { name: 'Google Pixel 3 XL', codename: 'crosshatch', image: 'https://raw.githubusercontent.com/Evolution-X/www_gitres/refs/heads/udc/devices/images/crosshatch.png', download: 'https://sourceforge.net/projects/evolution-x/files/crosshatch' },
    ],
    unofficial: [
      { name: 'Xiaomi Redmi 5 Plus', codename: 'vince', image: 'https://images.frandroid.com/wp-content/uploads/2019/04/xiaomi-redmi-5-plus-2018.png', download: 'https://roms.onelots.fr' },
    ],
  }

  return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 text-white">
        <header className="sticky top-0 z-50 bg-black/30 backdrop-blur-lg">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link href="/" className="flex items-center space-x-2">
              <Smartphone className="h-8 w-8 text-purple-400" />
              <span className="text-2xl font-bold">Onelots</span>
            </Link>
            <nav className="hidden md:flex space-x-8">
              <Link href="#about" className="hover:text-purple-400 transition-colors">About</Link>
              <Link href="#devices" className="hover:text-purple-400 transition-colors">Devices</Link>
              <Link href="#features" className="hover:text-purple-400 transition-colors">Features</Link>
              <Link href="/downloads" className="hover:text-purple-400 transition-colors">Download</Link>
            </nav>
            <Button onClick={() => setMenuOpen(!menuOpen)} className="md:hidden">
              {menuOpen ? <X /> : <Menu />}
            </Button>
          </div>
          {menuOpen && (
              <nav className="md:hidden bg-black/30 backdrop-blur-lg">
                <div className="container mx-auto px-4 py-4 flex flex-col space-y-4">
                  <Link href="#about" className="hover:text-purple-400 transition-colors">About</Link>
                  <Link href="#devices" className="hover:text-purple-400 transition-colors">Devices</Link>
                  <Link href="#features" className="hover:text-purple-400 transition-colors">Features</Link>
                  <Link href="/downloads" className="hover:text-purple-400 transition-colors">Download</Link>
                </div>
              </nav>
          )}
        </header>

        <main>
          <section className="py-20 md:py-32 text-center">
            <div className="container mx-auto px-4">
              <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in-up">Welcome to Onelots builds</h1>
              <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto animate-fade-in-up animation-delay-200">
                Official maintainer for EvolutionX, bringing you the best custom ROM experience.
              </p>
              <div className="space-x-4 animate-fade-in-up animation-delay-400">
                <Button asChild className="bg-purple-600 hover:bg-purple-700">
                  <Link href="#devices"> Explore Devices</Link>
                </Button>
                <Button asChild variant="outline" className="border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-white">
                  <Link href="https://wiki.evolution-x.org"> Learn More</Link>
                </Button>
              </div>
            </div>
          </section>

          <section id="about" className="py-20 bg-black/30 backdrop-blur-lg">
            <div className="container mx-auto px-4 text-center">
              <img
                  src="https://github.com/oneloutre.png"
                  alt="Profile"
                  className="rounded-full w-32 h-32 mx-auto mb-6"
              />
              <h2 className="text-3xl md:text-4xl font-bold mb-8">About Onelots</h2>
              <p className="text-lg md:text-xl max-w-3xl mx-auto">
                Onelots is a dedicated maintainer for EvolutionX, committed to providing high-quality custom ROM builds
                for a variety of Android devices. With a focus on performance, stability, and cutting-edge features, we
                strive to enhance your mobile experience.
              </p>
            </div>
          </section>


          <section id="devices" className="py-20">
            <div className="container mx-auto px-4">
              <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center">Supported Devices</h2>
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full max-w-3xl mx-auto">
                <TabsList className="grid w-full grid-cols-2 bg-black/30 backdrop-blur-lg rounded-full p-1 text-white">
                  <TabsTrigger value="official"
                               className="rounded-full data-[state=active]:bg-purple-600">Official</TabsTrigger>
                  <TabsTrigger value="unofficial"
                               className="rounded-full data-[state=active]:bg-purple-600">Unofficial</TabsTrigger>
                </TabsList>
                <TabsContent value="official" className="mt-8">
                  <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                    {devices.official.map((device) => (
                        <Card key={device.codename} className="bg-black/30 backdrop-blur-lg border-purple-500 hover:border-purple-400 transition-colors">
                          <CardHeader>
                            <CardTitle className="text-blue-200">
                              <a href={device.download} target="_blank" rel="noopener noreferrer">
                                {device.name}
                              </a>
                            </CardTitle>
                            <CardDescription className="text-purple-300">{device.codename}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <a href={device.download} target="_blank" rel="noopener noreferrer">
                              <img src={device.image} alt={device.name} className="w-full h-auto rounded-lg"/>
                            </a>
                          </CardContent>
                        </Card>
                    ))}
                  </div>
                </TabsContent>
                <TabsContent value="unofficial" className="mt-8">
                  <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                    {devices.unofficial.map((device) => (
                        <Card key={device.codename} className="bg-black/30 backdrop-blur-lg border-purple-500 hover:border-purple-400 transition-colors">
                          <CardHeader>
                            <CardTitle className="text-blue-200">
                              <a href={device.download} target="_blank" rel="noopener noreferrer">
                                {device.name}
                              </a>
                            </CardTitle>
                            <CardDescription className="text-purple-300">{device.codename}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <a href={device.download} target="_blank" rel="noopener noreferrer">
                              <img src={device.image} alt={device.name} className="w-full h-auto rounded-lg"/>
                            </a>
                          </CardContent>
                        </Card>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </section>

          <section id="features" className="py-20 bg-black/30 backdrop-blur-lg">
            <div className="container mx-auto px-4">
              <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center">EvolutionX Features</h2>
              <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                <Card className="bg-gradient-to-br from-purple-800 to-indigo-800 border-none">
                  <CardHeader>
                    <Cpu className="w-12 h-12 mb-4 text-purple-300" />
                    <CardTitle className="text-xl">Performance Optimizations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-purple-200">Enjoy smoother performance and better battery life with custom kernel tweaks.</p>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-indigo-800 to-blue-800 border-none">
                  <CardHeader>
                    <Smartphone className="w-12 h-12 mb-4 text-indigo-300" />
                    <CardTitle className="text-xl">Customization Options</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-indigo-200">Personalize your device with a wide range of customization features and themes.</p>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-800 to-purple-800 border-none">
                  <CardHeader>
                    <Zap className="w-12 h-12 mb-4 text-blue-300" />
                    <CardTitle className="text-xl">Regular Updates</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-blue-200">Stay up-to-date with the latest Android security patches and feature updates.</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>

          <section id="download" className="py-20 text-center">
            <div className="container mx-auto px-4">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Evolve?</h2>
              <p className="text-xl mb-8 max-w-2xl mx-auto">
                Download EvolutionX for your device, maintained by Onelots, and experience Android like never before.
              </p>
              <div className="flex flex-col space-y-4">
                <a href="https://sourceforge.net/projects/evolution-x/files/" download>
                  <Button className="bg-purple-600 hover:bg-purple-700 text-lg px-8 py-3">
                    <Download className="mr-2 h-5 w-5"/> Download Now
                  </Button>
                </a>
                <Link href="/downloads">
                  <Button className="bg-purple-600 hover:bg-purple-700 text-lg px-8 py-3">
                    <Copy className="mr-2 h-5 w-5" /> Download Now (Mirror)
                  </Button>
                </Link>
              </div>

            </div>
          </section>
        </main>

        <footer className="bg-black/30 backdrop-blur-lg py-8">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-sm text-purple-300 mb-4 md:mb-0">© 2024 Onelots. All rights reserved. (Jk it is on
                github)</p>
              <nav className="flex space-x-6 mb-4 md:mb-0">
              </nav>
              <div className="flex space-x-4">
                <Link href="https://github.com/Oneloutre" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Github className="h-6 w-6" />
                  <span className="sr-only">GitHub</span>
                </Link>
                <Link href="https://twitter.com/Onelots1" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Twitter className="h-6 w-6" />
                  <span className="sr-only">Twitter</span>
                </Link>
                <Link href="https://t.me/onelots" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Telegram />
                  <span className="sr-only">Telegram</span>
                </Link>
                <Link href="https://paypal.me/0nelots" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Paypal />
                  <span className="sr-only">Paypal</span>
                </Link>
                <Link href="https://discord.gg/evolution-x" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Discord />
                  <span className="sr-only">Discord</span>
                </Link>
                <Link href="mailto://onelots@onelots.fr" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Mail className="h-6 w-6" />
                  <span className="sr-only">Email</span>
                </Link>
                <Link href="https://roms.onelots.fr" target="_blank" rel="noopener noreferrer" className="text-purple-300 hover:text-white transition-colors">
                  <Copy className="h-6 w-6" />
                  <span className="sr-only">mirror</span>
                </Link>
              </div>
            </div>
          </div>
        </footer>
      </div>
  )
}
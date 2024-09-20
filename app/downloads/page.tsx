"use client";

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Folder, File, ChevronRight, Download, ArrowLeft, Grid, List, SortAsc, SortDesc, HardDrive, FileText, FolderOpen } from 'lucide-react'

type FileSystemItem = {
    name: string
    type: 'file' | 'directory'
    size: number
}

type ViewMode = 'grid' | 'list'
type SortOption = 'name' | 'type' | 'size'
type SortDirection = 'asc' | 'desc'

export default function EnhancedFileBrowserWithFolderSizes() {
    const [currentPath, setCurrentPath] = useState<string[]>(['EvolutionX'])
    const [currentContent, setCurrentContent] = useState<FileSystemItem[]>([])
    const [filteredContent, setFilteredContent] = useState<FileSystemItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [viewMode, setViewMode] = useState<ViewMode>('grid')
    const [searchTerm, setSearchTerm] = useState('')
    const [sortOption, setSortOption] = useState<SortOption>('name')
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
    const [stats, setStats] = useState({ totalSize: 0, fileCount: 0, folderCount: 0 })

    useEffect(() => {
        fetchDirectoryContents(currentPath.join('/'))
    }, [currentPath])

    useEffect(() => {
        const filtered = currentContent.filter(item =>
            item.name.toLowerCase().includes(searchTerm.toLowerCase())
        )
        const sorted = filtered.sort((a, b) => {
            if (sortOption === 'name') {
                return sortDirection === 'asc'
                    ? a.name.localeCompare(b.name)
                    : b.name.localeCompare(a.name)
            } else if (sortOption === 'type') {
                return sortDirection === 'asc'
                    ? a.type.localeCompare(b.type)
                    : b.type.localeCompare(a.type)
            } else {
                return sortDirection === 'asc'
                    ? a.size - b.size
                    : b.size - a.size
            }
        })
        setFilteredContent(sorted)

        const newStats = filtered.reduce((acc, item) => {
            if (item.type === 'file') {
                acc.fileCount++
            } else {
                acc.folderCount++
            }
            acc.totalSize += item.size
            return acc
        }, { totalSize: 0, fileCount: 0, folderCount: 0 })
        setStats(newStats)
    }, [currentContent, searchTerm, sortOption, sortDirection])

    const fetchDirectoryContents = async (path: string) => {
        setIsLoading(true)
        try {
            const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`)
            if (!response.ok) throw new Error('Failed to fetch directory contents')
            const data = await response.json()
            setCurrentContent(data)
        } catch (error) {
            console.error('Error fetching directory contents:', error)
            setCurrentContent([])
        } finally {
            setIsLoading(false)
        }
    }

    const navigateToFolder = (folderName: string) => {
        setCurrentPath([...currentPath, folderName])
    }

    const navigateUp = () => {
        if (currentPath.length > 1) {
            setCurrentPath(currentPath.slice(0, -1))
        }
    }

    const getFileIcon = (fileName: string) => {
        const extension = fileName.split('.').pop()?.toLowerCase()
        switch (extension) {
            case 'pdf':
                return <File className="text-red-400" />
            case 'jpg':
            case 'png':
            case 'gif':
                return <File className="text-green-400" />
            case 'mp3':
            case 'wav':
                return <File className="text-purple-400" />
            case 'zip':
            case 'rar':
                return <File className="text-yellow-400" />
            default:
                return <File className="text-blue-400" />
        }
    }

    const formatFileSize = (size: number) => {
        if (size < 1024) return `${size} B`
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
        if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)} MB`
        return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`
    }

    const handleItemClick = (item: FileSystemItem) => {
        if (item.type === 'directory') {
            navigateToFolder(item.name)
        } else {
            window.open(`/api/download?file=${encodeURIComponent(currentPath.join('/'))}/${encodeURIComponent(item.name)}`, '_blank')
        }
    }

    const toggleViewMode = () => {
        setViewMode(viewMode === 'grid' ? 'list' : 'grid')
    }

    const toggleSortDirection = () => {
        setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    }

    const renderItem = (item: FileSystemItem) => {
        return (
            <Card
                key={item.name}
                className={`bg-black/20 backdrop-blur-sm border-purple-500 hover:border-purple-400 transition-colors cursor-pointer ${viewMode === 'list' ? 'w-full' : ''}`}
                onClick={() => handleItemClick(item)}
            >
                <CardContent className={`p-4 flex items-center justify-between text-blue-200 ${viewMode === 'list' ? 'flex-row' : 'flex-col'}`}>
                    <div className={`flex items-center overflow-hidden ${viewMode === 'list' ? 'w-1/2' : 'w-full justify-center mb-2'}`}>
                        {item.type === 'directory' ? (
                            <Folder className="text-yellow-400 mr-2 flex-shrink-0" />
                        ) : (
                            getFileIcon(item.name)
                        )}
                        <span className={`ml-2 truncate ${viewMode === 'list' ? '' : 'text-center'}`}>{item.name}</span>
                    </div>
                    <div className={`flex items-center ${viewMode === 'list' ? 'w-1/2 justify-end' : 'w-full justify-between'}`}>
                        <span className="text-xs text-gray-400 mr-2">
                            {formatFileSize(item.size)}
                        </span>
                        {item.type === 'directory' ? (
                            <ChevronRight className="h-4 w-4" />
                        ) : (
                            <Download className="h-4 w-4" />
                        )}
                    </div>
                </CardContent>
            </Card>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 text-white p-8">
            <Card className="bg-black/30 backdrop-blur-lg border-purple-500 mb-6">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <Button
                            variant="ghost"
                            size="default"
                            onClick={() => window.location.href = '/'}
                            className="hover:bg-purple-700"
                        >
                            <ArrowLeft className="h-5 w-5 mr-2 text-cyan-200"/>
                            <p className="text-cyan-200 flex-auto font-bold">Back to website</p>
                        </Button>
                        <h1 className="text-2xl font-bold text-cyan-200 text-center flex-grow">Roms Downloading</h1>
                        <div className="w-40" />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-center">
                            <HardDrive className="h-8 w-8 mr-2 text-purple-400" />
                            <div>
                                <p className="text-sm text-gray-400">Total size</p>
                                <p className="text-lg font-semibold text-gray-300">{formatFileSize(stats.totalSize)}</p>
                            </div>
                        </div>
                        <div className="flex items-center">
                            <FileText className="h-8 w-8 mr-2 text-blue-400"/>
                            <div>
                                <p className="text-sm text-gray-400">Files</p>
                                <p className="text-lg font-semibold text-gray-300">{stats.fileCount}</p>
                            </div>
                        </div>
                        <div className="flex items-center">
                            <FolderOpen className="h-8 w-8 mr-2 text-yellow-400"/>
                            <div>
                                <p className="text-sm text-gray-400">Directories</p>
                                <p className="text-lg font-semibold text-gray-300">{stats.folderCount}</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
            <Card className="bg-black/30 backdrop-blur-lg border-purple-500">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={navigateUp}
                                disabled={currentPath.length === 1}
                                className="mr-2 hover:bg-purple-700"
                            >
                                <ArrowLeft className="h-4 w-4 text-cyan-200" />
                            </Button>
                            <h2 className="text-xl font-bold text-cyan-200">
                                /{currentPath.join('/')}
                            </h2>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={toggleViewMode}
                            className="hover:bg-purple-700"
                        >
                            {viewMode === 'grid' ? <List className="h-4 w-4 text-blue-200" /> : <Grid className="h-4 w-4 text-cyan-200" />}
                        </Button>
                    </div>
                    <div className="flex flex-col md:flex-row gap-4 mb-6">
                        <div className="flex-grow">
                            <Input
                                type="text"
                                placeholder="Search in the current directory..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full bg-black/20 border-purple-500 text-white placeholder-gray-400"
                            />
                        </div>
                        <div className="flex gap-2">
                            <Select value={sortOption} onValueChange={(value: SortOption) => setSortOption(value)}>
                                <SelectTrigger className="w-[180px] bg-black/20 border-purple-500 text-white">
                                    <SelectValue placeholder="Sort by" />
                                </SelectTrigger>
                                <SelectContent className="bg-black/80 border-purple-500 text-white">
                                    <SelectItem value="name">Name</SelectItem>
                                    <SelectItem value="type">Type</SelectItem>
                                    <SelectItem value="size">Size</SelectItem>
                                </SelectContent>
                            </Select>
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={toggleSortDirection}
                                className="border-purple-500 text-white hover:bg-purple-700"
                            >
                                {sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
                            </Button>
                        </div>
                    </div>
                    {isLoading ? (
                        <div className="text-center py-8">Loading...</div>
                    ) : (
                        <div className={viewMode === 'grid' ? 'grid gap-4 md:grid-cols-2 lg:grid-cols-3' : 'flex flex-col space-y-2'}>
                            {filteredContent.map(renderItem)}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
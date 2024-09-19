import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Fonction pour obtenir la taille totale d'un dossier de manière récursive
function getDirectorySize(directoryPath: string): number {
    let totalSize = 0;
    const items = fs.readdirSync(directoryPath);

    items.forEach(item => {
        const fullPath = path.join(directoryPath, item);
        const stats = fs.lstatSync(fullPath);

        if (stats.isDirectory()) {
            totalSize += getDirectorySize(fullPath); // Appel récursif
        } else {
            totalSize += stats.size; // Taille du fichier
        }
    });

    return totalSize;
}

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const requestedPath = searchParams.get('path');

    if (!requestedPath) {
        return NextResponse.json({ error: 'Invalid path parameter.' }, { status: 400 });
    }

    const baseDir = path.join(process.cwd(), 'public/');
    const directoryPath = path.join(baseDir, requestedPath);

    if (!directoryPath.startsWith(baseDir)) {
        return NextResponse.json({ error: 'Invalid path.' }, { status: 400 });
    }

    try {
        const items = fs.readdirSync(directoryPath).map((item) => {
            const fullPath = path.join(directoryPath, item);
            const isDirectory = fs.lstatSync(fullPath).isDirectory();

            return {
                name: item,
                type: isDirectory ? 'directory' : 'file',
                size: !isDirectory ? fs.statSync(fullPath).size : getDirectorySize(fullPath), // Calculer la taille du dossier
            };
        });

        return NextResponse.json(items, { status: 200 });
    } catch (error) {
        console.error('Error reading directory:', error);
        return NextResponse.json({ error: 'Failed to read directory.' }, { status: 500 });
    }
}

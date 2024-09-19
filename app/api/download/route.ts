import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const filePath = searchParams.get('file');

    if (!filePath) {
        return NextResponse.json({ error: 'File path is required.' }, { status: 400 });
    }

    const baseDir = path.join(process.cwd(), 'public/');

    const fullPath = path.join(baseDir, filePath);

    if (!fullPath.startsWith(baseDir)) {
        return NextResponse.json({ error: 'Invalid file path.' }, { status: 400 });
    }

    try {
        if (fs.existsSync(fullPath)) {
            const file = fs.readFileSync(fullPath);

            return new NextResponse(file, {
                headers: {
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': `attachment; filename="${path.basename(fullPath)}"`,
                },
            });
        } else {
            return NextResponse.json({ error: 'File not found.' }, { status: 404 });
        }
    } catch (error) {
        console.error('Error serving file:', error);
        return NextResponse.json({ error: 'Error serving the file.' }, { status: 500 });
    }
}

import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';

// Define the interface for the paths.json structure
interface PathsConfig {
    paths: string[];
    filters: string[];
}

// Function to read and process files
function generatePathOutput(configPath: string): void {
    try {
        // Read and parse the paths.json file
        const config: PathsConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

        // Initialize the output content
        let outputContent = '';

        // Process each path in the config
        for (const pattern of config.paths) {
            // Get all files matching the path pattern
            const files = glob.sync(pattern, { nodir: true });

            for (const file of files) {
                // Check if the file matches any of the filters
                const ext = path.extname(file);
                if (config.filters.some(filter => ext === path.extname(filter) || filter === ext)) {
                    // Read the file content
                    const content = fs.readFileSync(file, 'utf-8');
                    // Append to output in the required format
                    outputContent += `${file}\n${content}\n\n`;
                }
            }
        }

        // Write the output to path_output.txt
        fs.writeFileSync('path_output.txt', outputContent.trim());
        console.log('Successfully generated path_output.txt');
    } catch (error) {
        console.error('Error generating path output:', error);
    }
}

// Run the script with the paths.json file
generatePathOutput('paths.json');
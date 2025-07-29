#!/usr/bin/env node

/**
 * JSON Schema validation script for getLLM model metadata
 * This is a declarative test approach using JSON Schema
 */

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

// Initialize Ajv
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

// Load schema
const schemaPath = path.join(__dirname, 'model_schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

// Compile schema
const validate = ajv.compile(schema);

// Get home directory
const homeDir = process.env.HOME || process.env.USERPROFILE;

// Paths to validate
const filesToValidate = [
  path.join(homeDir, '.getllm', 'models', 'models_metadata.json'),
  path.join(homeDir, '.getllm', 'models', 'huggingface_models.json'),
  path.join(homeDir, '.getllm', 'models', 'ollama_models.json')
];

// Validate each file
filesToValidate.forEach(filePath => {
  console.log(`Validating ${filePath}...`);
  
  try {
    if (!fs.existsSync(filePath)) {
      console.log(`\x1b[33mFile does not exist: ${filePath}\x1b[0m`);
      return;
    }
    
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const valid = validate(data);
    
    if (valid) {
      console.log(`\x1b[32m✓ ${path.basename(filePath)} is valid!\x1b[0m`);
    } else {
      console.log(`\x1b[31m✗ ${path.basename(filePath)} validation failed!\x1b[0m`);
      console.log('Errors:');
      validate.errors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error.instancePath} ${error.message}`);
      });
    }
  } catch (error) {
    console.log(`\x1b[31mError processing ${filePath}: ${error.message}\x1b[0m`);
  }
  
  console.log('-----------------------------------');
});

// Check for Bielik models in Hugging Face cache
const hfCachePath = path.join(homeDir, '.getllm', 'models', 'huggingface_models.json');
if (fs.existsSync(hfCachePath)) {
  try {
    const hfData = JSON.parse(fs.readFileSync(hfCachePath, 'utf8'));
    const models = Array.isArray(hfData) ? hfData : (hfData.models || []);
    
    // Check for Bielik models
    const bielikModels = models.filter(model => 
      (model.name && model.name.toLowerCase().includes('bielik')) ||
      (model.id && model.id.toLowerCase().includes('bielik'))
    );
    
    if (bielikModels.length > 0) {
      console.log(`\x1b[32m✓ Found ${bielikModels.length} Bielik models in Hugging Face cache\x1b[0m`);
      bielikModels.forEach(model => {
        console.log(`  - ${model.name || model.id}`);
      });
    } else {
      console.log(`\x1b[33m⚠ No Bielik models found in Hugging Face cache\x1b[0m`);
    }
  } catch (error) {
    console.log(`\x1b[31mError checking for Bielik models: ${error.message}\x1b[0m`);
  }
}

console.log('\nTest complete!');

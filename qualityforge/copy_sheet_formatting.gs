/**
 * Google Apps Script to copy formatting from source spreadsheet to destination spreadsheet.
 * 
 * To use this script:
 * 1. Open the SOURCE spreadsheet: https://docs.google.com/spreadsheets/d/1M-hX9tNlGmXi-Efis05T35uftDkfR9w6QHg-kPM9h4g/edit
 * 2. Go to Extensions > Apps Script
 * 3. Paste this entire script
 * 4. Save and run the copyFormatting function
 * 5. Grant necessary permissions when prompted
 */

// Source spreadsheet (formatting guide)
const SOURCE_ID = "1M-hX9tNlGmXi-Efis05T35uftDkfR9w6QHg-kPM9h4g";
const SOURCE_SHEET_NAME = "Test Cases";

// Destination spreadsheet (to be formatted)
const DEST_ID = "1OwdsZEMWRS2hsweWGv546V14l4QhxV-KnIxjnBrsYSM";
const DEST_SHEET_NAME = "Test Cases";

/**
 * Main function to copy formatting from source to destination
 */
function copyFormatting() {
  const sourceSpreadsheet = SpreadsheetApp.openById(SOURCE_ID);
  const sourceSheet = sourceSpreadsheet.getSheetByName(SOURCE_SHEET_NAME);
  
  const destSpreadsheet = SpreadsheetApp.openById(DEST_ID);
  const destSheet = destSpreadsheet.getSheetByName(DEST_SHEET_NAME);
  
  if (!sourceSheet) {
    throw new Error(`Source sheet "${SOURCE_SHEET_NAME}" not found`);
  }
  
  if (!destSheet) {
    throw new Error(`Destination sheet "${DEST_SHEET_NAME}" not found`);
  }
  
  Logger.log("Starting formatting copy...");
  
  // Get dimensions
  const sourceLastRow = sourceSheet.getLastRow();
  const sourceLastCol = sourceSheet.getLastColumn();
  const destLastRow = destSheet.getLastRow();
  const destLastCol = destSheet.getLastColumn();
  
  Logger.log(`Source: ${sourceLastRow} rows x ${sourceLastCol} columns`);
  Logger.log(`Dest: ${destLastRow} rows x ${destLastCol} columns`);
  
  // Copy column widths
  copyColumnWidths(sourceSheet, destSheet, sourceLastCol);
  
  // Copy row heights for header
  copyRowHeight(sourceSheet, destSheet, 1);
  
  // Copy header row formatting (row 1)
  copyRowFormatting(sourceSheet, destSheet, 1, Math.min(sourceLastCol, destLastCol));
  
  // Copy data row formatting (use first data row as template for all rows)
  applyDataRowFormatting(sourceSheet, destSheet, destLastRow, Math.min(sourceLastCol, destLastCol));
  
  // Copy frozen rows/columns
  copyFrozenPanes(sourceSheet, destSheet);
  
  Logger.log("Formatting copy complete!");
  SpreadsheetApp.getActiveSpreadsheet().toast("Formatting copied successfully!", "Complete", 5);
}

/**
 * Copy column widths from source to destination
 */
function copyColumnWidths(sourceSheet, destSheet, numCols) {
  Logger.log(`Copying ${numCols} column widths...`);
  
  for (let col = 1; col <= numCols; col++) {
    const width = sourceSheet.getColumnWidth(col);
    destSheet.setColumnWidth(col, width);
  }
}

/**
 * Copy a single row's height
 */
function copyRowHeight(sourceSheet, destSheet, row) {
  const height = sourceSheet.getRowHeight(row);
  destSheet.setRowHeight(row, height);
}

/**
 * Copy formatting for a single row
 */
function copyRowFormatting(sourceSheet, destSheet, row, numCols) {
  Logger.log(`Copying formatting for row ${row}...`);
  
  const sourceRange = sourceSheet.getRange(row, 1, 1, numCols);
  const destRange = destSheet.getRange(row, 1, 1, numCols);
  
  // Copy text formatting
  destRange.setFontColors(sourceRange.getFontColors());
  destRange.setFontFamilies(sourceRange.getFontFamilies());
  destRange.setFontSizes(sourceRange.getFontSizes());
  destRange.setFontWeights(sourceRange.getFontWeights());
  destRange.setFontStyles(sourceRange.getFontStyles());
  
  // Copy cell formatting
  destRange.setBackgrounds(sourceRange.getBackgrounds());
  destRange.setHorizontalAlignments(sourceRange.getHorizontalAlignments());
  destRange.setVerticalAlignments(sourceRange.getVerticalAlignments());
  destRange.setWrapStrategies(sourceRange.getWrapStrategies());
}

/**
 * Apply data row formatting based on source template
 */
function applyDataRowFormatting(sourceSheet, destSheet, destLastRow, numCols) {
  if (destLastRow <= 1) {
    Logger.log("No data rows to format");
    return;
  }
  
  Logger.log(`Applying data row formatting to rows 2-${destLastRow}...`);
  
  // Get formatting from source row 2 (first data row)
  const sourceDataRow = sourceSheet.getRange(2, 1, 1, numCols);
  const destDataRange = destSheet.getRange(2, 1, destLastRow - 1, numCols);
  
  // Get source formatting
  const fontColors = sourceDataRow.getFontColors();
  const fontFamilies = sourceDataRow.getFontFamilies();
  const fontSizes = sourceDataRow.getFontSizes();
  const fontWeights = sourceDataRow.getFontWeights();
  const fontStyles = sourceDataRow.getFontStyles();
  const backgrounds = sourceDataRow.getBackgrounds();
  const hAlignments = sourceDataRow.getHorizontalAlignments();
  const vAlignments = sourceDataRow.getVerticalAlignments();
  const wrapStrategies = sourceDataRow.getWrapStrategies();
  
  // Expand to all rows
  const numRows = destLastRow - 1;
  const expandedFontColors = expandArray(fontColors, numRows);
  const expandedFontFamilies = expandArray(fontFamilies, numRows);
  const expandedFontSizes = expandArray(fontSizes, numRows);
  const expandedFontWeights = expandArray(fontWeights, numRows);
  const expandedFontStyles = expandArray(fontStyles, numRows);
  const expandedBackgrounds = expandArray(backgrounds, numRows);
  const expandedHAlignments = expandArray(hAlignments, numRows);
  const expandedVAlignments = expandArray(vAlignments, numRows);
  const expandedWrapStrategies = expandArray(wrapStrategies, numRows);
  
  // Apply formatting
  destDataRange.setFontColors(expandedFontColors);
  destDataRange.setFontFamilies(expandedFontFamilies);
  destDataRange.setFontSizes(expandedFontSizes);
  destDataRange.setFontWeights(expandedFontWeights);
  destDataRange.setFontStyles(expandedFontStyles);
  destDataRange.setBackgrounds(expandedBackgrounds);
  destDataRange.setHorizontalAlignments(expandedHAlignments);
  destDataRange.setVerticalAlignments(expandedVAlignments);
  destDataRange.setWrapStrategies(expandedWrapStrategies);
}

/**
 * Expand a single row array to multiple rows
 */
function expandArray(singleRowArray, numRows) {
  const result = [];
  for (let i = 0; i < numRows; i++) {
    result.push(singleRowArray[0].slice()); // Clone the row
  }
  return result;
}

/**
 * Copy frozen rows and columns settings
 */
function copyFrozenPanes(sourceSheet, destSheet) {
  const frozenRows = sourceSheet.getFrozenRows();
  const frozenCols = sourceSheet.getFrozenColumns();
  
  Logger.log(`Copying frozen panes: ${frozenRows} rows, ${frozenCols} columns`);
  
  destSheet.setFrozenRows(frozenRows);
  destSheet.setFrozenColumns(frozenCols);
}

/**
 * Test function to verify access to both spreadsheets
 */
function testAccess() {
  try {
    const source = SpreadsheetApp.openById(SOURCE_ID);
    Logger.log(`Source spreadsheet: ${source.getName()}`);
    
    const dest = SpreadsheetApp.openById(DEST_ID);
    Logger.log(`Destination spreadsheet: ${dest.getName()}`);
    
    Logger.log("Access verified for both spreadsheets!");
  } catch (e) {
    Logger.log(`Error: ${e.message}`);
  }
}

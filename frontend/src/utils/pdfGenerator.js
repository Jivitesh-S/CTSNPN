import { jsPDF } from "jspdf";
import QRCode from "qrcode";

export async function generateServiceTokenPdf(data = {}, autoDownload = true) {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const tokenId = data.token_id || data.tokenId || "CAN-8968";
  const orderId = data.order_id || data.orderId || "ORD-1003";
  const customerName = data.customer_name || data.customerName || "Valued Customer";
  const phone = data.phone || "+91 98401 23456";
  const modelName = data.model_name || data.modelName || "Samsung Galaxy Device";
  const requestType = data.request_type || data.requestType || "Cancellation";
  const price = data.price ? Number(data.price).toLocaleString() : "1,09,999";
  const purchaseDate = data.purchase_date || data.purchaseDate || "10-Aug-2026";
  const issueDate = new Date().toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  // Colors
  const primaryBlue = [0, 74, 198];
  const darkSlate = [15, 23, 42];
  const lightBg = [248, 250, 252];
  const borderGray = [226, 232, 240];
  const purpleAccent = [107, 56, 212];

  // Top Accent Banner
  doc.setFillColor(...primaryBlue);
  doc.rect(0, 0, 210, 8, "F");

  // Header Box
  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(...primaryBlue);
  doc.text("TECHSTORE RETAIL & SUPPORT", 14, 22);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.5);
  doc.setTextColor(100, 116, 139);
  doc.text("Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Tamil Nadu 600066", 14, 28);
  doc.text("Helpline: +91 90870 86182  |  Email: support@techstore.in  |  GSTIN: 33AAAAA0000A1Z5", 14, 33);

  // Horizontal separator
  doc.setDrawColor(...borderGray);
  doc.setLineWidth(0.5);
  doc.line(14, 38, 196, 38);

  // Document Title Badge
  doc.setFillColor(238, 242, 255);
  doc.roundedRect(14, 43, 182, 14, 2, 2, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(...purpleAccent);
  doc.text("OFFICIAL SERVICE TOKEN & E-INVOICE RECEIPT", 18, 52);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(16, 185, 129);
  doc.text("[AUTH: Telegram 2FA Verified]", 150, 52);

  // Metadata Grid (Token & Dates)
  doc.setFillColor(...lightBg);
  doc.roundedRect(14, 62, 182, 34, 2, 2, "F");
  doc.setDrawColor(...borderGray);
  doc.roundedRect(14, 62, 182, 34, 2, 2, "D");

  // Left Column
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...darkSlate);
  doc.text("Service Token #:", 18, 70);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...primaryBlue);
  doc.text(`#${tokenId}`, 50, 70);

  doc.setFont("helvetica", "bold");
  doc.setTextColor(...darkSlate);
  doc.text("Original Order #:", 18, 79);
  doc.setFont("helvetica", "normal");
  doc.text(`#${orderId}`, 50, 79);

  doc.setFont("helvetica", "bold");
  doc.text("Request Type:", 18, 88);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(225, 29, 72);
  doc.text(requestType.toUpperCase(), 50, 88);

  // Right Column
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...darkSlate);
  doc.text("Generated On:", 115, 70);
  doc.setFont("helvetica", "normal");
  doc.text(issueDate, 145, 70);

  doc.setFont("helvetica", "bold");
  doc.text("Customer Name:", 115, 79);
  doc.setFont("helvetica", "normal");
  doc.text(customerName, 145, 79);

  doc.setFont("helvetica", "bold");
  doc.text("Contact Phone:", 115, 88);
  doc.setFont("helvetica", "normal");
  doc.text(phone, 145, 88);

  // QR Code Generation onto PDF
  try {
    const qrData = data.qr_data || `TECHSTORE:TOKEN:${tokenId}:${orderId}:${phone}`;
    const qrDataUrl = await QRCode.toDataURL(qrData, { margin: 1, width: 120 });
    doc.addImage(qrDataUrl, "PNG", 162, 102, 30, 30);
    doc.setFontSize(6.5);
    doc.setTextColor(100, 116, 139);
    doc.text("Scan for Verification", 163, 134);
  } catch (qrErr) {
    console.error("QR Code generation in PDF failed:", qrErr);
  }

  // Items / Service Table Header
  const tableY = 104;
  doc.setFillColor(...primaryBlue);
  doc.rect(14, tableY, 142, 8, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.setTextColor(255, 255, 255);
  doc.text("ITEM / PRODUCT DETAILS", 18, tableY + 5.5);
  doc.text("PURCHASE DATE", 75, tableY + 5.5);
  doc.text("AMOUNT", 125, tableY + 5.5);

  // Table Row 1
  const rowY = tableY + 8;
  doc.setFillColor(255, 255, 255);
  doc.rect(14, rowY, 142, 22, "F");
  doc.setDrawColor(...borderGray);
  doc.rect(14, rowY, 142, 22, "D");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  doc.setTextColor(...darkSlate);
  doc.text(modelName, 18, rowY + 6.5);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7.5);
  doc.setTextColor(100, 116, 139);
  doc.text(`Category: Mobile/Electronics  |  Token Ref: ${tokenId}`, 18, rowY + 12);
  doc.text(`Location: Ambattur, Chennai (Store #S001)`, 18, rowY + 17);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(...darkSlate);
  doc.text(purchaseDate, 75, rowY + 8.5);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  doc.setTextColor(...darkSlate);
  doc.text(`Rs. ${price}`, 125, rowY + 8.5);

  // Summary Box
  const summaryY = 142;
  doc.setFillColor(...lightBg);
  doc.roundedRect(14, summaryY, 182, 34, 2, 2, "F");
  doc.setDrawColor(...borderGray);
  doc.roundedRect(14, summaryY, 182, 34, 2, 2, "D");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...primaryBlue);
  doc.text("IMPORTANT NEXT STEPS & STORE VERIFICATION:", 18, summaryY + 7);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(71, 85, 105);
  doc.text("1. Your request has been authenticated via Telegram OTP and recorded in our live Admin CRM.", 18, summaryY + 14);
  doc.text("2. Present this official receipt or QR code pass at TechStore store counter.", 18, summaryY + 20);
  doc.text("3. For service status or reverse pickup inquiry, please quote Service Token #" + tokenId + ".", 18, summaryY + 26);

  // Digital Signature & Authorization Stamp
  const footerY = 184;
  doc.setDrawColor(...borderGray);
  doc.line(14, footerY, 196, footerY);

  doc.setFont("helvetica", "italic");
  doc.setFontSize(7.5);
  doc.setTextColor(148, 163, 184);
  doc.text("This is a computer-generated official electronic invoice and requires no physical signature.", 14, footerY + 6);
  doc.text(`Generated securely by TechStore Assistant • System ID: TS-SYS-${tokenId} • Country: India (IN)`, 14, footerY + 11);

  // Auth Badge Stamp on bottom right
  doc.setFillColor(240, 253, 244);
  doc.roundedRect(140, footerY + 3, 56, 12, 1.5, 1.5, "F");
  doc.setDrawColor(187, 247, 208);
  doc.roundedRect(140, footerY + 3, 56, 12, 1.5, 1.5, "D");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(7);
  doc.setTextColor(22, 101, 52);
  doc.text("✔ DIGITALLY VERIFIED", 145, footerY + 8);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(6);
  doc.text("Telegram 2FA Authenticated", 145, footerY + 12);

  const filename = `TechStore_Invoice_${tokenId}.pdf`;

  if (autoDownload) {
    doc.save(filename);
  }

  return doc;
}

export async function generateReservationInvoicePdf(data = {}, autoDownload = true) {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const tokenId = data.token_id || data.tokenId || "RES-1001";
  const customerName = data.customer_name || data.customerName || "Customer";
  const phone = data.phone || "+91 9087086182";
  const productName = data.product_name || data.productName || "Samsung Galaxy Device";
  const price = data.price ? Number(data.price).toLocaleString() : "1,34,999";
  const holdHours = data.hold_hours || 24;
  const storeAddress = data.store_address || "Ambattur Red Hills Rd, Velammal Nagar, Surapet, Chennai, Tamil Nadu 600066";
  const storePhone = data.store_phone || "+91 9087086182";
  
  const issueDate = new Date().toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  // Colors
  const primaryBlue = [0, 74, 198];
  const darkSlate = [15, 23, 42];
  const lightBg = [248, 250, 252];
  const borderGray = [226, 232, 240];

  // Top Banner
  doc.setFillColor(...primaryBlue);
  doc.rect(0, 0, 210, 8, "F");

  // Store Brand Header with Flag
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(...primaryBlue);
  doc.text("TECHSTORE RETAIL & WALK-IN EXPERIENCE", 14, 22);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.5);
  doc.setTextColor(100, 116, 139);
  doc.text(`${storeAddress}  |  Flag: India (IN)`, 14, 28);
  doc.text(`Helpline: ${storePhone}  |  Store Timings: 10:00 AM - 9:00 PM Daily`, 14, 33);

  // Divider
  doc.setDrawColor(...borderGray);
  doc.line(14, 38, 196, 38);

  // Title Box
  doc.setFillColor(238, 242, 255);
  doc.roundedRect(14, 43, 182, 14, 2, 2, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(79, 70, 229);
  doc.text("OFFICIAL IN-STORE 24-HOUR RESERVATION PASS & INVOICE", 18, 52);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(16, 185, 129);
  doc.text("[AUTH: Telegram OTP Verified]", 145, 52);

  // Pass Information Box
  doc.setFillColor(...lightBg);
  doc.roundedRect(14, 62, 182, 34, 2, 2, "F");
  doc.setDrawColor(...borderGray);
  doc.roundedRect(14, 62, 182, 34, 2, 2, "D");

  // Left Details
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...darkSlate);
  doc.text("Reservation Token #:", 18, 70);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...primaryBlue);
  doc.text(`#${tokenId}`, 56, 70);

  doc.setFont("helvetica", "bold");
  doc.setTextColor(...darkSlate);
  doc.text("Customer Name:", 18, 79);
  doc.setFont("helvetica", "normal");
  doc.text(customerName, 56, 79);

  doc.setFont("helvetica", "bold");
  doc.text("Contact Mobile:", 18, 88);
  doc.setFont("helvetica", "normal");
  doc.text(phone, 56, 88);

  // Right Details
  doc.setFont("helvetica", "bold");
  doc.text("Issued Date & Time:", 115, 70);
  doc.setFont("helvetica", "normal");
  doc.text(issueDate, 150, 70);

  doc.setFont("helvetica", "bold");
  doc.text("Hold Duration:", 115, 79);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(225, 29, 72);
  doc.text(`${holdHours} Hours (Guaranteed Stock)`, 150, 79);

  doc.setFont("helvetica", "bold");
  doc.setTextColor(...darkSlate);
  doc.text("Store Location:", 115, 88);
  doc.setFont("helvetica", "normal");
  doc.text("Surapet, Chennai (S001)", 150, 88);

  // Generate QR Code onto PDF
  try {
    const qrPayload = data.qr_data || `TECHSTORE:PASS:${tokenId}:${productName}:${phone}`;
    const qrDataUrl = await QRCode.toDataURL(qrPayload, { margin: 1, width: 140 });
    doc.addImage(qrDataUrl, "PNG", 158, 102, 34, 34);
    doc.setFontSize(7);
    doc.setTextColor(100, 116, 139);
    doc.text("In-Store Scanner Pass", 158, 139);
  } catch (qrErr) {
    console.error("QR Code creation failed:", qrErr);
  }

  // Reserved Item Table Header
  const tableY = 104;
  doc.setFillColor(...primaryBlue);
  doc.rect(14, tableY, 138, 8, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.setTextColor(255, 255, 255);
  doc.text("RESERVED DEVICE MODEL", 18, tableY + 5.5);
  doc.text("HOLD STATUS", 80, tableY + 5.5);
  doc.text("STORE PRICE", 120, tableY + 5.5);

  // Table Row
  const rowY = tableY + 8;
  doc.setFillColor(255, 255, 255);
  doc.rect(14, rowY, 138, 24, "F");
  doc.setDrawColor(...borderGray);
  doc.rect(14, rowY, 138, 24, "D");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  doc.setTextColor(...darkSlate);
  doc.text(productName, 18, rowY + 6.5);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7.5);
  doc.setTextColor(100, 116, 139);
  doc.text(`Official TechStore Catalog Device • Brand: Samsung`, 18, rowY + 12);
  doc.text(`Includes 12–24 Months Official Manufacturer Warranty`, 18, rowY + 17);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.setTextColor(22, 101, 52);
  doc.text("ACTIVE HOLD (24H)", 80, rowY + 8.5);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...darkSlate);
  doc.text(`Rs. ${price}`, 120, rowY + 8.5);

  // Terms & Pickup Box
  const summaryY = 146;
  doc.setFillColor(...lightBg);
  doc.roundedRect(14, summaryY, 182, 34, 2, 2, "F");
  doc.setDrawColor(...borderGray);
  doc.roundedRect(14, summaryY, 182, 34, 2, 2, "D");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...primaryBlue);
  doc.text("IN-STORE CLAIM INSTRUCTIONS:", 18, summaryY + 7);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(71, 85, 105);
  doc.text("1. Present this digital/printed E-Invoice pass or Token ID #" + tokenId + " at TechStore checkout.", 18, summaryY + 14);
  doc.text("2. Payment can be made at the store via UPI, Card, Cash, or 0% EMI.", 18, summaryY + 20);
  doc.text("3. Your device is held for 24 hours. For questions, call +91 90870 86182.", 18, summaryY + 26);

  // Footer Signature & Stamp
  const footerY = 188;
  doc.setDrawColor(...borderGray);
  doc.line(14, footerY, 196, footerY);

  doc.setFont("helvetica", "italic");
  doc.setFontSize(7.5);
  doc.setTextColor(148, 163, 184);
  doc.text("This is an authenticated reservation pass. No physical signature required.", 14, footerY + 6);
  doc.text(`Issued securely by TechStore Assistant • Pass Ref: TS-RES-${tokenId}`, 14, footerY + 11);

  // Digital Stamp
  doc.setFillColor(240, 253, 244);
  doc.roundedRect(140, footerY + 3, 56, 12, 1.5, 1.5, "F");
  doc.setDrawColor(187, 247, 208);
  doc.roundedRect(140, footerY + 3, 56, 12, 1.5, 1.5, "D");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(7);
  doc.setTextColor(22, 101, 52);
  doc.text("✔ RESERVATION VERIFIED", 143, footerY + 8);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(6);
  doc.text("2FA Authenticated Hold", 143, footerY + 12);

  const filename = `TechStore_Reservation_${tokenId}.pdf`;

  if (autoDownload) {
    doc.save(filename);
  }

  return doc;
}

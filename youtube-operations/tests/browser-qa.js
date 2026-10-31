const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless:true,args:['--no-sandbox']});
  try {
    const page=await browser.newPage({acceptDownloads:true});
    const failures=[];
    page.on('pageerror',e=>failures.push(e.message));
    await page.goto('http://127.0.0.1:8765/',{waitUntil:'domcontentloaded'});
    assert.match(await page.title(),/YouTube Operations/);
    await page.locator('#channel').fill('SSAG Browser QA');
    await page.locator('#titleInput').fill('Real working thumbnail and job tracker');
    await page.locator('#description').fill('An original content plan prepared for QA testing.');
    await page.locator('#createJob').click();
    assert.equal(await page.locator('#jobs .task').count(),1);
    assert.equal(await page.locator('#countAll').textContent(),'1');
    await page.locator('#thumbHeadline').fill('SSAG CHANNEL TEST');
    await page.locator('#renderThumbnail').click();
    const thumb=page.waitForEvent('download');
    await page.locator('#saveThumbnail').click();
    const dl=await thumb;
    assert.match(dl.suggestedFilename(),/\.png$/);
    await page.locator('#supportChannel').fill('SSAG Browser QA');
    await page.locator('#supportTitle').fill('Please review the upload schedule.');
    await page.locator('#openTicket').click();
    assert.equal(await page.locator('#tickets .task').count(),1);
    assert.equal(await page.locator('#countSupport').textContent(),'1');
    const csv=page.waitForEvent('download');
    await page.locator('#exportReport').click();
    assert.match((await csv).suggestedFilename(),/\.csv$/);
    await page.locator('#downloadPack').click();
    assert.match(await page.locator('#exportStatus').textContent(),/approval/i);
    assert.deepEqual(failures,[]);
    console.log('REAL BROWSER PASS: weekly content job, local counters, PNG thumbnail, support ticket, CSV export, rights/approval blocker.');
  } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});

import * as constants from '../../constants';
import * as t from '../../types';
import { setTimeout } from "timers/promises";

describe("noi/paramChanges.ts", () => {
    let page;

    beforeAll(async () => {
        page = await globalThis.__BROWSER_GLOBAL__.newPage();

        // page.on("console", message => console.log(message.text()));

        await global.wait.runserverInit();
        await page.setDefaultNavigationTimeout(0);
    });

    it("test #5792", async () => {
        await page.goto(global.SERVER_URL);
        await global.signIn(page);
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({pathname: "/api/tickets/MyTicketsToWork"})
        });
        // await global.wait.dataLoadDone(page);
        await page.waitForNetworkIdle();
        await page.evaluate((c) => {
            window.App.URLContext.actionHandler.update({values: {
                assigned_toHidden: 6
            }, windowType: c.WINDOW_TYPE_PARAMS})
        }, constants);
        await page.waitForNetworkIdle();

        await page.waitForSelector("div.l-detail-header>span");
        let header = await page.$("div.l-detail-header>span");
        let headerText = await (await header.getProperty("textContent")).jsonValue();

        expect(headerText).toBe("Tickets to work (Assigned to Luc)")

        await header.dispose();

        // await global.waitToMeet(page, () => {
        //     let t = document.querySelector('div.l-detail-header>span').textContent;
        //     // console.log(t);
        //     return t === "Tickets to work (Assigned to Luc)";
        // });
        await page.locator('div.l-grid p.clearfix a').click();
        await page.waitForNetworkIdle();

        header = await page.$("div.l-detail-header>span");
        headerText = await (await header.getProperty("textContent")).jsonValue();

        expect(headerText).toBe("Tickets to work (Assigned to Luc) » #101 (Foo never bars)");
        header.dispose();

        // await global.waitToMeet(page, () => {
        //     const header = document.querySelector('div.l-detail-header>span');
        //     if (!header) return false;
        //     let t = header.textContent;
        //     // console.log(t)
        //     return t === "Tickets to work (Assigned to Luc) » #101 (Foo never bars)";
        // })

        const commentsValue = await page.evaluate(() => window.App.URLContext
            .dataContext.refStore.slaveLeaves["comments.CommentsByRFC"].state.value);

        expect(commentsValue).not.toBe(null);
    })

    afterAll(async () => {
        await page.close();
    })
})

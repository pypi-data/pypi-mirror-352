import * as t from '../../types';
import * as constants from "../../constants";
import { setTimeout } from "timers/promises";

describe("noi/URLContext.ts", () => {
    let page;

    beforeAll(async () => {
        page = await globalThis.__BROWSER_GLOBAL__.newPage();
        // page.on("console", message => console.log(message.text()));
        await global.wait.runserverInit();
        await page.setDefaultNavigationTimeout(0);
    });

    beforeEach(async () => {
        await page.goto(global.SERVER_URL);
        await page.waitForNetworkIdle();
        await global.signIn(page);
    });

    // it.skip("trading.InvoicesByJournal workflow button", async () => {
    it("trading.InvoicesByJournal workflow button", async () => {
        await page.evaluate(() => {
             window.App.state.menu_data.filter(
                 md => md.label === 'Sales'
             )[0].items.filter(
                 md => md.label === 'Sales invoices (SLS)'
             )[0].command();
        });
        await page.waitForNetworkIdle();

        const invoice_id = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.rows[0][
                window.App.URLContext.static.actorData.pk_index
            ];
        });

        await page.evaluate((pk) => {
            window.App.URLContext.actionHandler.singleRow({}, pk);
        }, invoice_id);
        await page.waitForNetworkIdle();

        await page.evaluate((pk) => {
            window.App.URLContext.actionHandler.runAction({
                actorId: "trading.InvoicesByJournal", an: "wf2", sr: pk
            })
        }, invoice_id)
        await page.waitForNetworkIdle();

        // const clone = await page.evaluate(() => {
        //     return window.App.URLContext.actionHandler.parser.stringify({
        //         clone: {
        //             params: {path: "/api/trading/InvoicesByJournal/86", mk: 1, mt: 66},
        //             runnable: {actorId: "trading.InvoicesByJournal", an: "wf2", sr: 86},
        //         }
        //     }, true);
        // });
        // await page.goBack();  // Otherwise, browser doesn't load the hash content from the following goto.
        // // 127.0.0.1:8000/#/api/trading/InvoicesByJournal/86?clone=JSON%3A%3A%3A%7B%22params%22%3A%7B%22path%22%3A%22%2Fapi%2Ftrading%2FInvoicesByJournal%2F86%22%2C%22mk%22%3A1%2C%22mt%22%3A72%7D%2C%22runnable%22%3A%7B%22actorId%22%3A%22trading.InvoicesByJournal%22%2C%22an%22%3A%22wf2%22%2C%22sr%22%3A86%7D%7D
        // await page.goto(`${global.SERVER_URL}/#/api/trading/InvoicesByJournal/86?${clone}`);
        // await page.waitForNetworkIdle();

        let wfState;
        wfState = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.data.workflow_buttons;
        });
        expect(wfState).toContain("<b>Draft</b>");
        await page.evaluate((pk) => {
            window.App.URLContext.actionHandler.runAction({
                actorId: "trading.InvoicesByJournal", an: "wf1", sr: pk
            });
        }, invoice_id);
        await page.waitForNetworkIdle();
        wfState = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.data.workflow_buttons;
        });
        expect(wfState).toContain("<b>Registered</b>");
    });

    // it.skip("test grid_put", async () => {
    it("test grid_put", async () => {
        await page.evaluate((c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {[c.URL_PARAM_DISPLAY_MODE]: c.DISPLAY_MODE_TABLE}
            });
        }, constants);
        await page.waitForNetworkIdle();

        let firstSummary = await page.$(".l-grid-col-summary");
        await firstSummary.click();
        await firstSummary.waitForSelector('input');
        let input = await firstSummary.$('input');
        const oldSummary = await (await input.getProperty('value')).jsonValue();
        await input.dispose();

        const inputText = "Nothing important to say!";

        await firstSummary.type(inputText);
        await page.keyboard.press("Enter");
        await page.waitForNetworkIdle();
        await firstSummary.dispose();

        firstSummary = await page.$(".l-grid-col-summary");
        await firstSummary.click();
        await firstSummary.waitForSelector('input');

        input = await firstSummary.$("input");
        const newSummary = await (await input.getProperty('value')).jsonValue();
        await input.dispose();

        expect(newSummary).toBe(inputText);

        await firstSummary.type(oldSummary);
        await page.keyboard.press("Enter");
        await page.waitForNetworkIdle();

        await firstSummary.dispose();
    });

    it("TicketsByParent ticket.description open in own window", async () => {
        await page.evaluate((c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {[c.URL_PARAM_LIMIT]: 100}
            })
        }, constants);
        await page.waitForNetworkIdle();


        const rows = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.rows;
        });

        for (var i = 0; i < rows.length; i++) {
            const row = rows[i];
            await page.evaluate((pk) => {
                window.App.URLContext.history.pushPath({
                    pathname: `/api/tickets/AllTickets/${pk}`,
                    params: {tab: 2}
                });
            }, row.id);
            await page.waitForNetworkIdle();

            const childRows = await page.evaluate((t) => {
                return (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                    .dataContext.mutableContext.rows;
            }, t);
            if (childRows.length) {
                await page.evaluate((pk) => {
                    (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                        .actionHandler.singleRow({}, pk, window.App.URLContext);
                }, childRows[0].id);
                await page.waitForNetworkIdle();
                break;
            }
        }

        await page.evaluate(() => {
            window.App.URLContext.history.replace({tab: 1});
        });

        await page.locator('span ::-p-text(⏏)').click();
        await page.waitForNetworkIdle();

        const success = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.success;
        })
        expect(success).toBe(true);

        const master_key = await page.evaluate((c) => {
            return window.App.URLContext.value[c.URL_PARAM_MASTER_PK];
        }, constants);
        expect(typeof master_key).toEqual("number");

        const master_type = await page.evaluate((c) => {
            return window.App.URLContext.value[c.URL_PARAM_MASTER_TYPE];
        }, constants);
        expect(typeof master_type).toEqual("number");

        const contextType = await page.evaluate(() => {
            return window.App.URLContext.contextType;
        });
        expect(contextType).toEqual(constants.CONTEXT_TYPE_TEXT_FIELD);
    });

    afterAll(async () => {
        await page.close();
    })
});

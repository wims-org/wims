FROM mcr.microsoft.com/playwright:v1.54.0-noble

COPY package.json /workspaces/integration/package.json
COPY package-lock.json /workspaces/integration/package-lock.json
COPY playwright.config.ts /workspaces/integration/playwright.config.ts
COPY tests /workspaces/integration/tests
COPY helpers /workspaces/integration/helpers

RUN ls -l /workspaces/integration/

WORKDIR /workspaces/integration
RUN npm install
RUN npx playwright install --with-deps

CMD ["npx", "playwright", "test"]
VOLUME ["/workspaces/integration/test-results"]
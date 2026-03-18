const token = process.env.RUQI_CLIENT_MCP_TOKEN;
const env = process.env.RUQI_CLIENT_ENV || "test";

const config = {
  pollInterval: 5000,
  env: {
    dev: "dev",
    test: "test",
    uat: "uat",
    prod: "prod",
  },
  baseUrl: {
    dev: "https://devdocker-clientapi.ruqimobility.com/mcp/v1",
    test: "https://testdocker-clientapi.ruqimobility.com/mcp/v1",
    uat: "https://uatdocker-clientapi.ruqimobility.com/mcp/v1",
    prod: "https://docker-clientapi.ruqimobility.com/mcp/v1",
  },
  passengerH5Url: {
    dev: "https://webdev.ruqimobility.com/ruqi/index.html#/",
    test: "https://webtest.ruqimobility.com/ruqi/index.html#/",
    uat: "https://webrel.ruqimobility.com/ruqi/index.html#/",
    prod: "https://web.ruqimobility.com/ruqi/index.html#/",
  },
  feishu: {
    appId: "cli_a93e6de474e11bb6",
    appSecret: "M55dL9XUROOY3sY3QsG4Wdh2SFtBLtAV",
  },
};

export { token, env, config };

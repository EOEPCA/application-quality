# Application Quality Service Frontend

These instructions help get you started developing the Application Quality Service frontend with Vue 3 in Vite.

## Suggested IDE Setup

[VSCodium](https://vscodium.com/): Community-driven, freely-licensed binary distribution of Microsoft’s editor VSCode.

Microsoft’s editor [VSCode](https://code.visualstudio.com/).

VSCode / VSCodium extension [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
# Packages needed for development and production are installed by default 
npm install

# To only install packages needed for production (see how to build, below)
npm install --omit=dev
```

### Compile and Hot-Reload for Development

This starts a local server at http://localhost:3000

```sh
npm run dev
```

### Execute Tests

Test scripts use the [Vitest](https://vitest.dev/) testing framework.

```sh
# List the existing tests
npm run test:list

# Execute the tests once then exit
npm run test

# Execute the tests and watch for changes
npm run test:watch
```

### Lint with [ESLint](https://eslint.org/)

```sh
# Perform a dry-run: display problems without trying to fix them
npm run lint

# Try to fix the problems and display the ones that cannot be fixed automatically
npm run lint:write
```

### Format the code with [Prettier](https://prettier.io/)

```sh
# Display changes without applying them
npm run format

# Format the code and apply changes
npm run format:write
```

### Compile and Minify for Production

The result is stored in the `dist` subfolder.

```sh
npm run build
```

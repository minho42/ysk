<template>
  <nav id="navbar">
    <header
      class="bg-white dark:bg-gray-900 flex justify-between border-b border-gray-300 dark:border-gray-500 shadow-sm">
      <div class="flex items-center justify-between pl-3 py-2 h-16">
        <div class="flex items-center">
          <NuxtLink to="/" class="px-1 py-1 font-semibold text-lg dark:text-white dark:hover:text-gray-300">
            호주 역송금 비교
          </NuxtLink>
        </div>
      </div>
      <div class="px-2 py-2 flex items-center" style="touch-action: manipulation;">
          <NuxtLink to="/about"
          class="dark:text-white block px-3 py-2 ml-2 text-lg text-center rounded-lg border-none border-t border-gray-300 hover:bg-gray-200 dark:hover:bg-transparent dark:hover:text-gray-300 mt-0">
          About</NuxtLink>
        </div>
    </header>
  </nav>
</template>

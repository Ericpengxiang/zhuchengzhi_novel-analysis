// 通用交互脚本

// 高亮当前页面对应的导航
(function highlightNav() {
  try {
    const path = location.pathname.split("/").pop() || "";
    const links = document.querySelectorAll(".nav-link[data-page]");
    links.forEach((link) => {
      const page = link.getAttribute("data-page");
      if (page && path.indexOf(page) !== -1) {
        link.classList.add("active");
      }
      link.addEventListener("click", function (e) {
        const target = this.getAttribute("data-href");
        if (target) {
          e.preventDefault();
          window.location.href = target;
        }
      });
    });
  } catch (e) {
    console.warn(e);
  }
})();

// 显示当前登录用户名或登录/注册按钮
(function injectUserName() {
  const nameEl = document.querySelector("[data-fake-user]");
  const headerRight = document.querySelector(".main-header-right");
  if (!nameEl || !headerRight) return;

  // 从API获取用户信息
  fetch('/api/novel/auth/info/', {
    credentials: 'include'
  })
  .then(response => response.json())
  .then(result => {
    if (result.code === 200 && result.data) {
      // 已登录，显示用户名
      const username = result.data.nickname || result.data.username;
      nameEl.textContent = username;
      // 更新下拉菜单中的用户名
      const dropdownHeader = document.querySelector('.user-dropdown-header');
      if (dropdownHeader) {
        dropdownHeader.textContent = username;
      }
      // 确保头像显示
      const avatar = headerRight.querySelector('.avatar');
      if (avatar) {
        avatar.style.display = 'block';
      }
      // 移除登录/注册按钮（如果存在）
      const authButtons = headerRight.querySelector('.auth-buttons');
      if (authButtons) {
        authButtons.remove();
      }
    } else {
      // 未登录，显示登录/注册按钮
      nameEl.textContent = "游客";
      // 隐藏头像
      const avatar = headerRight.querySelector('.avatar');
      if (avatar) {
        avatar.style.display = 'none';
      }
      // 检查是否已有登录/注册按钮
      let authButtons = headerRight.querySelector('.auth-buttons');
      if (!authButtons) {
        authButtons = document.createElement('div');
        authButtons.className = 'auth-buttons';
        authButtons.innerHTML = `
          <button class="auth-btn auth-btn-login" onclick="showLoginModal()">登录</button>
          <button class="auth-btn auth-btn-register" onclick="showRegisterModal()">注册</button>
        `;
        // 插入到用户名后面
        const nameContainer = nameEl.parentElement;
        if (nameContainer && nameContainer.nextSibling) {
          nameContainer.parentNode.insertBefore(authButtons, nameContainer.nextSibling);
        } else {
          headerRight.appendChild(authButtons);
        }
      }
    }
  })
  .catch(() => {
    // 网络错误，显示游客和登录/注册按钮
    nameEl.textContent = "游客";
    const avatar = headerRight.querySelector('.avatar');
    if (avatar) {
      avatar.style.display = 'none';
    }
    let authButtons = headerRight.querySelector('.auth-buttons');
    if (!authButtons) {
      authButtons = document.createElement('div');
      authButtons.className = 'auth-buttons';
      authButtons.innerHTML = `
        <button class="auth-btn auth-btn-login" onclick="showLoginModal()">登录</button>
        <button class="auth-btn auth-btn-register" onclick="showRegisterModal()">注册</button>
      `;
      const nameContainer = nameEl.parentElement;
      if (nameContainer && nameContainer.nextSibling) {
        nameContainer.parentNode.insertBefore(authButtons, nameContainer.nextSibling);
      } else {
        headerRight.appendChild(authButtons);
      }
    }
  });
})();

// 收藏按钮切换
function toggleFavorite(btn) {
  if (!btn) return;
  const active = btn.getAttribute("data-active") === "1";
  if (active) {
    btn.textContent = "收藏";
    btn.setAttribute("data-active", "0");
  } else {
    btn.textContent = "取消收藏";
    btn.setAttribute("data-active", "1");
  }
}

// 头像下拉菜单
(function setupAvatarDropdown() {
  const avatar = document.querySelector('.avatar');
  if (!avatar) return;

  // 创建下拉菜单容器
  const container = document.createElement('div');
  container.className = 'avatar-container';
  avatar.parentNode.insertBefore(container, avatar);
  container.appendChild(avatar);

  // 创建下拉菜单
  const dropdown = document.createElement('div');
  dropdown.className = 'user-dropdown';
  
  // 初始用户名，稍后会通过API更新
  const nameEl = document.querySelector("[data-fake-user]");
  const initialUsername = nameEl ? (nameEl.textContent || '用户') : '用户';
  
  dropdown.innerHTML = `
    <div class="user-dropdown-header">${initialUsername}</div>
    <a href="/profile/" class="user-dropdown-item">个人信息</a>
    <a href="/favorites/" class="user-dropdown-item">用户收藏</a>
    <button class="user-dropdown-item" data-action="logout">退出登录</button>
  `;
  
  container.appendChild(dropdown);
  
  // 延迟更新用户名（等待API返回）
  setTimeout(() => {
    const updatedNameEl = document.querySelector("[data-fake-user]");
    if (updatedNameEl && updatedNameEl.textContent && updatedNameEl.textContent !== '用户') {
      const dropdownHeader = dropdown.querySelector('.user-dropdown-header');
      if (dropdownHeader) {
        dropdownHeader.textContent = updatedNameEl.textContent;
      }
    }
  }, 500);

  // 点击头像切换菜单显示
  avatar.addEventListener('click', function(e) {
    e.stopPropagation();
    dropdown.classList.toggle('show');
  });

  // 点击菜单项
  dropdown.addEventListener('click', function(e) {
    const item = e.target.closest('.user-dropdown-item');
    if (!item) return;

    const action = item.getAttribute('data-action');
    if (action === 'logout') {
      e.preventDefault();
      if (confirm('确定要退出登录吗？')) {
        fetch('/api/novel/auth/logout/', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then(response => response.json())
        .then(result => {
          if (result.code === 200) {
            dropdown.classList.remove('show');
            // 刷新页面以更新用户信息显示
            window.location.reload();
          } else {
            alert('退出失败：' + (result.message || '未知错误'));
          }
        })
        .catch(error => {
          console.error('退出登录失败:', error);
          dropdown.classList.remove('show');
          window.location.reload();
        });
      }
    } else {
      // 其他菜单项（个人信息、用户收藏）直接跳转
      dropdown.classList.remove('show');
    }
  });

  // 点击页面其他地方关闭菜单
  document.addEventListener('click', function(e) {
    if (!container.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
})();


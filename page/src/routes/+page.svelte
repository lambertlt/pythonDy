<script>
	import { onMount } from 'svelte';
	let data = {};
	let list = [];
	onMount(() => {
		getAllParams();
	});

	function getAllParams() {
		fetch('http://localhost:5000/params/all', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then((response) => {
				if (!response.ok) {
					throw new Error('Network response was not ok');
				}
				return response.json(); // 解析JSON数据
			})
			.then((json) => {
				data = json;
				list = Object.keys(data);
				console.log(list); // 确保在数据更新后执行
			})
			.catch((error) => console.error('Error:', error));
	}

	function setParams() {
		// 使用 fetch 发起 POST 请求
		fetch('http://localhost:5000/set_param', {
			method: 'POST', // 指定请求方法为 POST
			headers: {
				'Content-Type': 'application/json' // 设置请求头，告知服务器请求体是 JSON 格式
			},
			body: JSON.stringify({ ua_user: '123' }) // 将 JavaScript 对象转换为 JSON 字符串
		})
			.then((response) => response.json()) // 解析响应体为 JSON
			.then((data) => console.log(data)) // 处理服务器返回的数据
			.catch((error) => console.error('Error:', error)); // 错误处理
	}
</script>

<div class="form-container">
	{#each list as item, index}
		<div class="form-group">
			<label for="param4">{item}</label>
			<input type="text" id="param4" name="param4" required value={data[item]}/>
		</div>
	{/each}
	<button type="submit">提交</button>
</div>

<style>
	body {
		font-family: Arial, sans-serif;
		margin: 0;
		padding: 0;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		background-color: #f0f0f0;
	}
	.form-container {
		background-color: white;
		padding: 20px;
		border-radius: 8px;
		box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
		display: flex;
		flex-wrap: wrap;
	}
	.form-group {
		margin: 15px 31px;
	}
	label {
		display: block;
		margin-bottom: 5px;
	}
	input[type='text'],
	input[type='email'],
	input[type='password'] {
		width: 300px;
		padding: 8px;
		box-sizing: border-box;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
	button {
		width: 100%;
		padding: 10px;
		background-color: #5cb85c;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}
	button:hover {
		background-color: #4cae4c;
	}
</style>

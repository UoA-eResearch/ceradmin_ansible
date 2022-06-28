<html>
    <head>
    </head>
    <body>
      Dear {{ item.first_name }},
      <br><br>
      Thank you for consenting to grant University of Auckland Nectar operational
      staff access to your Nectar VM(s) for vulnerability scanning for project
      <i>{{ item.project_name }}</i>.
      <br><br>
      We will initially install the vulnerability scanner on Linux VMs.
      <br><br>
      You have the following Linux VM(s) with a public IP address:
      <br><br>

      <table  border="3" width=auto style="border-collapse: collapse;">
      <tr>
          <th>VM name</th>
          <th>Nectar ID</th>
          <th>Operating System</th>
      </tr>
      {% for server in item.servers %}
      <tr>
        <td>{{ server['name'] }}</td>
        <td>{{ server['id'] }}</td>
        <td>{{ server['metadata']['os_family'] }} {{ server['metadata']['os_version'] }}</td>
      </tr>
      {% endfor %}
    </table>
    <br>
    To enable the installation of the vulnerability scanner we need you to configure
    a public SSH key on the VM(s), as described on the following page:
    <br><br>
    https://support.ehelp.edu.au/support/solutions/articles/6000256293-university-of-auckland-specific-configure-operator-public-ssh-key
    <br><br>
    Please let us know once this is done, and don't hesitate to get in touch you are
    not certain what we're asking for.
    <br><br><br>

    Many thanks,<br>
    Nectar@Auckland team, at the Centre for eResearch
  </body>
</html>
